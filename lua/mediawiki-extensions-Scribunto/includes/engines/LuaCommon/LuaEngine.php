<?php

use Wikimedia\ScopedCallback;

abstract class Scribunto_LuaEngine extends ScribuntoEngineBase {
	/**
	 * Libraries to load. See also the 'ScribuntoExternalLibraries' hook.
	 * @var array Maps module names to PHP classes or definition arrays
	 */
	protected static $libraryClasses = [
		'mw.site' => Scribunto_LuaSiteLibrary::class,
		'mw.uri' => Scribunto_LuaUriLibrary::class,
		'mw.ustring' => Scribunto_LuaUstringLibrary::class,
		'mw.language' => Scribunto_LuaLanguageLibrary::class,
		'mw.message' => Scribunto_LuaMessageLibrary::class,
		'mw.title' => Scribunto_LuaTitleLibrary::class,
		'mw.text' => Scribunto_LuaTextLibrary::class,
		'mw.html' => Scribunto_LuaHtmlLibrary::class,
		'mw.hash' => Scribunto_LuaHashLibrary::class,
	];

	/**
	 * Paths for modules that may be loaded from Lua. See also the
	 * 'ScribuntoExternalLibraryPaths' hook.
	 * @var array Paths
	 */
	protected static $libraryPaths = [
		'.',
		'luabit',
		'ustring',
	];

	protected $loaded = false;

	/**
	 * @var Scribunto_LuaInterpreter|null
	 */
	protected $interpreter;

	/**
	 * @var array
	 */
	protected $mw;

	/**
	 * @var array
	 */
	protected $currentFrames = [];
	protected $expandCache = [];
	protected $availableLibraries = [];

	const MAX_EXPAND_CACHE_SIZE = 100;

	/**
	 * If luasandbox is installed and usable then use it,
	 * otherwise
	 *
	 * @param array $options
	 * @return Scribunto_LuaEngine
	 */
	public static function newAutodetectEngine( array $options ) {
		global $wgScribuntoEngineConf;
		$engine = 'luastandalone';
		try {
			Scribunto_LuaSandboxInterpreter::checkLuaSandboxVersion();
			$engine = 'luasandbox';
		} catch ( Scribunto_LuaInterpreterNotFoundError $e ) {
			// pass
		} catch ( Scribunto_LuaInterpreterBadVersionError $e ) {
			// pass
		}

		unset( $options['factory'] );

		return Scribunto::newEngine( $options + $wgScribuntoEngineConf[$engine] );
	}

	/**
	 * Create a new interpreter object
	 * @return Scribunto_LuaInterpreter
	 */
	abstract protected function newInterpreter();

	/**
	 * @param string $text
	 * @param string|bool $chunkName
	 * @return Scribunto_LuaModule
	 */
	protected function newModule( $text, $chunkName ) {
		return new Scribunto_LuaModule( $this, $text, $chunkName );
	}

	/**
	 * @param string $message
	 * @param array $params
	 * @return Scribunto_LuaError
	 */
	public function newLuaError( $message, $params = [] ) {
		return new Scribunto_LuaError( $message, $this->getDefaultExceptionParams() + $params );
	}

	public function destroy() {
		// Break reference cycles
		$this->interpreter = null;
		$this->mw = [];
		$this->expandCache = null;
		parent::destroy();
	}

	/**
	 * Initialise the interpreter and the base environment
	 */
	public function load() {
		if ( $this->loaded ) {
			return;
		}
		$this->loaded = true;

		try {
			$this->interpreter = $this->newInterpreter();

			$funcs = [
				'loadPackage',
				'loadPHPLibrary',
				'frameExists',
				'newChildFrame',
				'getExpandedArgument',
				'getAllExpandedArguments',
				'expandTemplate',
				'callParserFunction',
				'preprocess',
				'incrementExpensiveFunctionCount',
				'isSubsting',
				'getFrameTitle',
				'setTTL',
				'addWarning',
			];

			$lib = [];
			foreach ( $funcs as $name ) {
				$lib[$name] = [ $this, $name ];
			}

			$this->registerInterface( 'mwInit.lua', [] );
			$this->mw = $this->registerInterface( 'mw.lua', $lib,
				[ 'allowEnvFuncs' => $this->options['allowEnvFuncs'] ] );

			$this->availableLibraries = $this->getLibraries( 'lua', self::$libraryClasses );
			foreach ( $this->availableLibraries as $name => $def ) {
				$this->instantiatePHPLibrary( $name, $def, false );
			}
		} catch ( Exception $ex ) {
			$this->loaded = false;
			$this->interpreter = null;
			throw $ex;
		}
	}

	/**
	 * Register a Lua Library
	 *
	 * This should be called from the library's PHP module's register() method.
	 *
	 * The value for $interfaceFuncs is used to populate the mw_interface
	 * global that is defined when the library's Lua module is loaded. Values
	 * must be PHP callables, which will be seen in Lua as functions.
	 *
	 * @param string $moduleFileName The path to the Lua portion of the library
	 *         (absolute, or relative to $this->getLuaLibDir())
	 * @param array $interfaceFuncs Populates mw_interface
	 * @param array $setupOptions Passed to the modules setupInterface() method.
	 * @return array Lua package
	 */
	public function registerInterface( $moduleFileName, $interfaceFuncs, $setupOptions = [] ) {
		$this->interpreter->registerLibrary( 'mw_interface', $interfaceFuncs );
		$moduleFileName = $this->normalizeModuleFileName( $moduleFileName );
		$package = $this->loadLibraryFromFile( $moduleFileName );
		if ( !empty( $package['setupInterface'] ) ) {
			$this->interpreter->callFunction( $package['setupInterface'], $setupOptions );
		}
		return $package;
	}

	/**
	 * Return the base path for Lua modules.
	 * @return string
	 */
	public function getLuaLibDir() {
		return __DIR__ . '/lualib';
	}

	/**
	 * Normalize a lua module to its full path. If path does not look like an
	 * absolute path (i.e. begins with DIRECTORY_SEPARATOR or "X:"), prepend
	 * getLuaLibDir()
	 *
	 * @param string $fileName name of the lua module file
	 * @return string
	 */
	protected function normalizeModuleFileName( $fileName ) {
		if ( !preg_match( '<^(?:[a-zA-Z]:)?' . preg_quote( DIRECTORY_SEPARATOR ) . '>', $fileName ) ) {
			$fileName = "{$this->getLuaLibDir()}/{$fileName}";
		}
		return $fileName;
	}

	/**
	 * Get performance characteristics of the Lua engine/interpreter
	 *
	 * phpCallsRequireSerialization: boolean
	 *   whether calls between PHP and Lua functions require (slow)
	 *   serialization of parameters and return values
	 *
	 * @return array
	 */
	abstract public function getPerformanceCharacteristics();

	/**
	 * Get the current interpreter object
	 * @return Scribunto_LuaInterpreter
	 */
	public function getInterpreter() {
		$this->load();
		return $this->interpreter;
	}

	/**
	 * Replaces the list of current frames, and return a ScopedCallback that
	 * will reset them when it goes out of scope.
	 *
	 * @param PPFrame|null $frame If null, an empty frame with no parent will be used
	 * @return ScopedCallback
	 */
	private function setupCurrentFrames( PPFrame $frame = null ) {
		if ( !$frame ) {
			$frame = $this->getParser()->getPreprocessor()->newFrame();
		}

		$oldFrames = $this->currentFrames;
		$oldExpandCache = $this->expandCache;
		$this->currentFrames = [
			'current' => $frame,
			'parent' => $frame->parent ?? null,
		];
		$this->expandCache = [];

		return new ScopedCallback( function () use ( $oldFrames, $oldExpandCache ) {
			$this->currentFrames = $oldFrames;
			$this->expandCache = $oldExpandCache;
		} );
	}

	/**
	 * Execute a module chunk in a new isolated environment, and return the specified function
	 * @param mixed $chunk As accepted by Scribunto_LuaInterpreter::callFunction()
	 * @param string $functionName
	 * @param PPFrame|null $frame
	 * @return mixed
	 * @throws ScribuntoException
	 */
	public function executeModule( $chunk, $functionName, $frame ) {
		// $resetFrames is a ScopedCallback, so it has a purpose even though it appears unused.
		$resetFrames = $this->setupCurrentFrames( $frame );

		$retval = $this->getInterpreter()->callFunction(
			$this->mw['executeModule'], $chunk, $functionName
		);
		if ( !$retval[0] ) {
			// If we get here, it means we asked for an element from the table the module returned,
			// but it returned something other than a table. In this case, $retval[1] contains the type
			// of what it did returned, instead of the value we asked for.
			throw $this->newException(
				'scribunto-lua-notarrayreturn', [ 'args' => [ $retval[1] ] ]
			);
		}
		return $retval[1];
	}

	/**
	 * Execute a module function chunk
	 * @param mixed $chunk As accepted by Scribunto_LuaInterpreter::callFunction()
	 * @param PPFrame|null $frame
	 * @return array
	 */
	public function executeFunctionChunk( $chunk, $frame ) {
		// $resetFrames is a ScopedCallback, so it has a purpose even though it appears unused.
		$resetFrames = $this->setupCurrentFrames( $frame );

		return $this->getInterpreter()->callFunction(
			$this->mw['executeFunction'],
			$chunk );
	}

	/**
	 * Get data logged by modules
	 * @return string Logged data
	 */
	protected function getLogBuffer() {
		if ( !$this->loaded ) {
			return '';
		}
		try {
			$log = $this->getInterpreter()->callFunction( $this->mw['getLogBuffer'] );
			return $log[0];
		} catch ( ScribuntoException $ex ) {
			// Probably time expired, ignore it.
			return '';
		}
	}

	/**
	 * Format the logged data for HTML output
	 * @param string $logs Logged data
	 * @param bool $localize Whether to localize the message key
	 * @return string HTML
	 */
	protected function formatHtmlLogs( $logs, $localize ) {
		$keyMsg = wfMessage( 'scribunto-limitreport-logs' );
		if ( !$localize ) {
			$keyMsg->inLanguage( 'en' )->useDatabase( false );
		}
		return Html::openElement( 'tr' ) .
			Html::rawElement( 'th', [ 'colspan' => 2 ], $keyMsg->parse() ) .
			Html::closeElement( 'tr' ) .
			Html::openElement( 'tr' ) .
			Html::openElement( 'td', [ 'colspan' => 2 ] ) .
			Html::openElement( 'div', [ 'class' => 'mw-collapsible mw-collapsed' ] ) .
			Html::element( 'pre', [ 'class' => 'scribunto-limitreport-logs' ], $logs ) .
			Html::closeElement( 'div' ) .
			Html::closeElement( 'td' ) .
			Html::closeElement( 'tr' );
	}

	/**
	 * Load a library from the given file and execute it in the base environment.
	 * @param string $fileName File name/path to load
	 * @return array|null the export list, or null if there isn't one.
	 */
	protected function loadLibraryFromFile( $fileName ) {
		static $cache = null;

		if ( !$cache ) {
			$cache = ObjectCache::getLocalServerInstance( 'hash' );
		}

		$mtime = filemtime( $fileName );
		if ( $mtime === false ) {
			throw new MWException( 'Lua file does not exist: ' . $fileName );
		}

		$cacheKey = $cache->makeGlobalKey( __CLASS__, $fileName );
		$fileData = $cache->get( $cacheKey );

		$code = false;
		if ( $fileData ) {
			list( $code, $cachedMtime ) = $fileData;
			if ( $cachedMtime < $mtime ) {
				$code = false;
			}
		}
		if ( !$code ) {
			$code = file_get_contents( $fileName );
			if ( $code === false ) {
				throw new MWException( 'Lua file does not exist: ' . $fileName );
			}
			$cache->set( $cacheKey, [ $code, $mtime ], 60 * 5 );
		}

		# Prepending an "@" to the chunk name makes Lua think it is a filename
		$module = $this->getInterpreter()->loadString( $code, '@' . basename( $fileName ) );
		$ret = $this->getInterpreter()->callFunction( $module );
		return $ret[0] ?? null;
	}

	/** @inheritDoc */
	public function getGeSHiLanguage() {
		return 'lua';
	}

	/** @inheritDoc */
	public function getCodeEditorLanguage() {
		return 'lua';
	}

	/** @inheritDoc */
	public function runConsole( array $params ) {
		// $resetFrames is a ScopedCallback, so it has a purpose even though it appears unused.
		$resetFrames = $this->setupCurrentFrames();

		/**
		 * TODO: provide some means for giving correct line numbers for errors
		 * in console input, and for producing an informative error message
		 * if there is an error in prevQuestions.
		 *
		 * Maybe each console line could be evaluated as a different chunk,
		 * apparently that's what lua.c does.
		 */
		$code = "return function (__init, exe)\n" .
			"if not exe then exe = function(...) return true, ... end end\n" .
			"local p = select(2, exe(__init) )\n" .
			"__init, exe = nil, nil\n" .
			"local print = mw.log\n";
		foreach ( $params['prevQuestions'] as $q ) {
			if ( substr( $q, 0, 1 ) === '=' ) {
				$code .= "print(" . substr( $q, 1 ) . ")";
			} else {
				$code .= $q;
			}
			$code .= "\n";
		}
		$code .= "mw.clearLogBuffer()\n";
		if ( substr( $params['question'], 0, 1 ) === '=' ) {
			// Treat a statement starting with "=" as a return statement, like in lua.c
			$code .= "local ret = mw.allToString(" . substr( $params['question'], 1 ) . ")\n" .
				"return ret, mw.getLogBuffer()\n";
		} else {
			$code .= $params['question'] . "\n" .
				"return nil, mw.getLogBuffer()\n";
		}
		$code .= "end\n";

		if ( $params['title']->hasContentModel( CONTENT_MODEL_SCRIBUNTO ) ) {
			$contentModule = $this->newModule(
				$params['content'], $params['title']->getPrefixedDBkey() );
			$contentInit = $contentModule->getInitChunk();
			$contentExe = $this->mw['executeModule'];
		} else {
			$contentInit = $params['content'];
			$contentExe = null;
		}

		$consoleModule = $this->newModule(
			$code,
			wfMessage( 'scribunto-console-current-src' )->text()
		);
		$consoleInit = $consoleModule->getInitChunk();
		$ret = $this->getInterpreter()->callFunction( $this->mw['executeModule'], $consoleInit, false );
		$func = $ret[1];
		$ret = $this->getInterpreter()->callFunction( $func, $contentInit, $contentExe );

		return [
			'return' => $ret[0] ?? null,
			'print' => $ret[1] ?? '',
		];
	}

	/**
	 * Workalike for luaL_checktype()
	 *
	 * @param string $funcName The Lua function name, for use in error messages
	 * @param array $args The argument array
	 * @param int $index0 The zero-based argument index
	 * @param string|array $type The allowed type names as given by gettype()
	 * @param string $msgType The type name used in the error message
	 * @throws Scribunto_LuaError
	 */
	public function checkType( $funcName, $args, $index0, $type, $msgType ) {
		if ( !is_array( $type ) ) {
			$type = [ $type ];
		}
		if ( !isset( $args[$index0] ) || !in_array( gettype( $args[$index0] ), $type, true ) ) {
			$index1 = $index0 + 1;
			throw new Scribunto_LuaError( "bad argument #$index1 to '$funcName' ($msgType expected)" );
		}
	}

	/**
	 * Workalike for luaL_checkstring()
	 *
	 * @param string $funcName The Lua function name, for use in error messages
	 * @param array $args The argument array
	 * @param int $index0 The zero-based argument index
	 */
	public function checkString( $funcName, $args, $index0 ) {
		$this->checkType( $funcName, $args, $index0, 'string', 'string' );
	}

	/**
	 * Workalike for luaL_checknumber()
	 *
	 * @param string $funcName The Lua function name, for use in error messages
	 * @param array $args The argument array
	 * @param int $index0 The zero-based argument index
	 */
	public function checkNumber( $funcName, $args, $index0 ) {
		$this->checkType( $funcName, $args, $index0, [ 'integer', 'double' ], 'number' );
	}

	/**
	 * Instantiate and register a library.
	 * @param string $name
	 * @param array|string $def
	 * @param bool $loadDeferred
	 * @throws MWException
	 * @return array|null
	 */
	private function instantiatePHPLibrary( $name, $def, $loadDeferred ) {
		$def = $this->availableLibraries[$name];
		if ( is_string( $def ) ) {
			$class = new $def( $this );
		} else {
			if ( !$loadDeferred && !empty( $def['deferLoad'] ) ) {
				return null;
			}
			if ( isset( $def['class'] ) ) {
				$class = new $def['class']( $this );
			} else {
				throw new MWException( "No class for library \"$name\"" );
			}
		}
		return $class->register();
	}

	/**
	 * Handler for the loadPHPLibrary() callback. Register the specified
	 * library and return its function table. It's not necessary to cache the
	 * function table in the object instance, since there is caching in a
	 * wrapper on the Lua side.
	 * @internal
	 * @param string $name
	 * @return array
	 */
	public function loadPHPLibrary( $name ) {
		$args = func_get_args();
		$this->checkString( 'loadPHPLibrary', $args, 0 );

		$ret = null;
		if ( isset( $this->availableLibraries[$name] ) ) {
			$ret = $this->instantiatePHPLibrary( $name, $this->availableLibraries[$name], true );
		}

		return [ $ret ];
	}

	/**
	 * Handler for the loadPackage() callback. Load the specified
	 * module and return its chunk. It's not necessary to cache the resulting
	 * chunk in the object instance, since there is caching in a wrapper on the
	 * Lua side.
	 * @internal
	 * @param string $name
	 * @return array
	 */
	public function loadPackage( $name ) {
		$args = func_get_args();
		$this->checkString( 'loadPackage', $args, 0 );

		# This is what Lua does for its built-in loaders
		$luaName = str_replace( '.', '/', $name ) . '.lua';
		$paths = $this->getLibraryPaths( 'lua', self::$libraryPaths );
		foreach ( $paths as $path ) {
			$fileName = $this->normalizeModuleFileName( "$path/$luaName" );
			if ( !file_exists( $fileName ) ) {
				continue;
			}
			$code = file_get_contents( $fileName );
			$init = $this->interpreter->loadString( $code, "@$luaName" );
			return [ $init ];
		}

		$title = Title::newFromText( $name );
		if ( !$title || !$title->hasContentModel( CONTENT_MODEL_SCRIBUNTO ) ) {
			return [];
		}

		$module = $this->fetchModuleFromParser( $title );
		if ( $module ) {
			// @phan-suppress-next-line PhanUndeclaredMethod
			return [ $module->getInitChunk() ];
		} else {
			return [];
		}
	}

	/**
	 * Helper function for the implementation of frame methods
	 *
	 * @param string $frameId
	 * @return PPFrame
	 *
	 * @throws Scribunto_LuaError
	 */
	protected function getFrameById( $frameId ) {
		if ( $frameId === 'empty' ) {
			return $this->getParser()->getPreprocessor()->newFrame();
		} elseif ( isset( $this->currentFrames[$frameId] ) ) {
			return $this->currentFrames[$frameId];
		} else {
			throw new Scribunto_LuaError( 'invalid frame ID' );
		}
	}

	/**
	 * Handler for frameExists()
	 *
	 * @internal
	 * @param string $frameId
	 * @return array
	 */
	public function frameExists( $frameId ) {
		return [ $frameId === 'empty' || isset( $this->currentFrames[$frameId] ) ];
	}

	/**
	 * Handler for newChildFrame()
	 *
	 * @internal
	 * @param string $frameId
	 * @param string $title
	 * @param array $args
	 * @return array
	 * @throws Scribunto_LuaError
	 */
	public function newChildFrame( $frameId, $title, array $args ) {
		if ( count( $this->currentFrames ) > 100 ) {
			throw new Scribunto_LuaError( 'newChild: too many frames' );
		}

		$frame = $this->getFrameById( $frameId );
		if ( $title === false ) {
			$title = $frame->getTitle();
		} else {
			$title = Title::newFromText( $title );
			if ( !$title ) {
				throw new Scribunto_LuaError( 'newChild: invalid title' );
			}
		}
		$args = $this->getParser()->getPreprocessor()->newPartNodeArray( $args );
		$newFrame = $frame->newChild( $args, $title );
		$newFrameId = 'frame' . count( $this->currentFrames );
		$this->currentFrames[$newFrameId] = $newFrame;
		return [ $newFrameId ];
	}

	/**
	 * Handler for getTitle()
	 *
	 * @internal
	 * @param string $frameId
	 *
	 * @return array
	 */
	public function getFrameTitle( $frameId ) {
		$frame = $this->getFrameById( $frameId );
		return [ $frame->getTitle()->getPrefixedText() ];
	}

	/**
	 * Handler for setTTL()
	 * @internal
	 * @param int $ttl
	 */
	public function setTTL( $ttl ) {
		$args = func_get_args();
		$this->checkNumber( 'setTTL', $args, 0 );

		$frame = $this->getFrameById( 'current' );
		$frame->setTTL( $ttl );
	}

	/**
	 * Handler for getExpandedArgument()
	 * @internal
	 * @param string $frameId
	 * @param string $name
	 * @return array
	 */
	public function getExpandedArgument( $frameId, $name ) {
		$args = func_get_args();
		$this->checkString( 'getExpandedArgument', $args, 0 );

		$frame = $this->getFrameById( $frameId );
		$this->getInterpreter()->pauseUsageTimer();
		$result = $frame->getArgument( $name );
		if ( $result === false ) {
			return [];
		} else {
			return [ $result ];
		}
	}

	/**
	 * Handler for getAllExpandedArguments()
	 * @internal
	 * @param string $frameId
	 * @return array
	 */
	public function getAllExpandedArguments( $frameId ) {
		$frame = $this->getFrameById( $frameId );
		$this->getInterpreter()->pauseUsageTimer();
		return [ $frame->getArguments() ];
	}

	/**
	 * Handler for expandTemplate()
	 * @internal
	 * @param string $frameId
	 * @param string $titleText
	 * @param array $args
	 * @return array
	 * @throws Scribunto_LuaError
	 */
	public function expandTemplate( $frameId, $titleText, $args ) {
		$frame = $this->getFrameById( $frameId );
		$title = Title::newFromText( $titleText, NS_TEMPLATE );
		if ( !$title ) {
			throw new Scribunto_LuaError( "expandTemplate: invalid title \"$titleText\"" );
		}

		if ( $frame->depth >= $this->parser->mOptions->getMaxTemplateDepth() ) {
			throw new Scribunto_LuaError( 'expandTemplate: template depth limit exceeded' );
		}
		if ( MWNamespace::isNonincludable( $title->getNamespace() ) ) {
			throw new Scribunto_LuaError( 'expandTemplate: template inclusion denied' );
		}

		list( $dom, $finalTitle ) = $this->parser->getTemplateDom( $title );
		if ( $dom === false ) {
			throw new Scribunto_LuaError( "expandTemplate: template \"$titleText\" does not exist" );
		}
		if ( !$frame->loopCheck( $finalTitle ) ) {
			throw new Scribunto_LuaError( 'expandTemplate: template loop detected' );
		}

		$fargs = $this->getParser()->getPreprocessor()->newPartNodeArray( $args );
		$newFrame = $frame->newChild( $fargs, $finalTitle );
		$text = $this->doCachedExpansion( $newFrame, $dom,
			[
				'frameId' => $frameId,
				'template' => $finalTitle->getPrefixedDBkey(),
				'args' => $args
			] );
		return [ $text ];
	}

	/**
	 * Handler for callParserFunction()
	 * @internal
	 * @param string $frameId
	 * @param string $function
	 * @param array $args
	 * @throws MWException
	 * @throws Scribunto_LuaError
	 * @return array
	 * @suppress PhanImpossibleCondition
	 */
	public function callParserFunction( $frameId, $function, $args ) {
		$frame = $this->getFrameById( $frameId );

		# Make zero-based, without screwing up named args
		$args = array_merge( [], $args );

		# Sort, since we can't rely on the order coming in from Lua
		uksort( $args, function ( $a, $b ) {
			if ( is_int( $a ) !== is_int( $b ) ) {
				return is_int( $a ) ? -1 : 1;
			}
			if ( is_int( $a ) ) {
				return $a - $b;
			}
			return strcmp( $a, $b );
		} );

		# Be user-friendly
		$colonPos = strpos( $function, ':' );
		if ( $colonPos !== false ) {
			array_unshift( $args, trim( substr( $function, $colonPos + 1 ) ) );
			$function = substr( $function, 0, $colonPos );
		}
		if ( !isset( $args[0] ) ) {
			# It's impossible to call a parser function from wikitext without
			# supplying an arg 0. Insist that one be provided via Lua, too.
			throw new Scribunto_LuaError( 'callParserFunction: At least one unnamed parameter ' .
				'(the parameter that comes after the colon in wikitext) ' .
				'must be provided'
			);
		}

		$result = $this->parser->callParserFunction( $frame, $function, $args );
		if ( !$result['found'] ) {
			throw new Scribunto_LuaError( "callParserFunction: function \"$function\" was not found" );
		}

		# Set defaults for various flags
		$result += [
			'nowiki' => false,
			'isChildObj' => false,
			'isLocalObj' => false,
			'isHTML' => false,
			'title' => false,
		];

		$text = $result['text'];
		if ( $result['isChildObj'] ) {
			$fargs = $this->getParser()->getPreprocessor()->newPartNodeArray( $args );
			$newFrame = $frame->newChild( $fargs, $result['title'] );
			if ( $result['nowiki'] ) {
				$text = $newFrame->expand( $text, PPFrame::RECOVER_ORIG );
			} else {
				$text = $newFrame->expand( $text );
			}
		}
		if ( $result['isLocalObj'] && $result['nowiki'] ) {
			$text = $frame->expand( $text, PPFrame::RECOVER_ORIG );
			$result['isLocalObj'] = false;
		}

		# Replace raw HTML by a placeholder
		if ( $result['isHTML'] ) {
			$text = $this->parser->insertStripItem( $text );
		} elseif ( $result['nowiki'] ) {
			# Escape nowiki-style return values
			// @phan-suppress-next-line SecurityCheck-DoubleEscaped
			$text = wfEscapeWikiText( $text );
		}

		if ( $result['isLocalObj'] ) {
			$text = $frame->expand( $text );
		}

		return [ "$text" ];
	}

	/**
	 * Handler for preprocess()
	 * @internal
	 * @param string $frameId
	 * @param string $text
	 * @return array
	 * @throws Scribunto_LuaError
	 */
	public function preprocess( $frameId, $text ) {
		$args = func_get_args();
		$this->checkString( 'preprocess', $args, 0 );

		$frame = $this->getFrameById( $frameId );

		if ( !$frame ) {
			throw new Scribunto_LuaError( 'attempt to call mw.preprocess with no frame' );
		}

		// Don't count the time for expanding all the frame arguments against
		// the Lua time limit.
		$this->getInterpreter()->pauseUsageTimer();
		$frame->getArguments();
		$this->getInterpreter()->unpauseUsageTimer();

		$text = $this->doCachedExpansion( $frame, $text,
			[
				'frameId' => $frameId,
				'inputText' => $text
			] );
		return [ $text ];
	}

	/**
	 * Increment the expensive function count, and throw if limit exceeded
	 *
	 * @internal
	 * @throws Scribunto_LuaError
	 * @return null
	 */
	public function incrementExpensiveFunctionCount() {
		if ( !$this->getParser()->incrementExpensiveFunctionCount() ) {
			throw new Scribunto_LuaError( "too many expensive function calls" );
		}
		return null;
	}

	/**
	 * Adds a warning to be displayed upon preview
	 *
	 * @internal
	 * @param string $text wikitext
	 */
	public function addWarning( $text ) {
		$this->getParser()->getOutput()->addWarning( $text );
	}

	/**
	 * Return whether the parser is currently substing
	 *
	 * @internal
	 * @return array
	 */
	public function isSubsting() {
		// See Parser::braceSubstitution, OT_WIKI is the switch
		return [ $this->getParser()->OutputType() === Parser::OT_WIKI ];
	}

	/**
	 * @param PPFrame $frame
	 * @param string|array $input
	 * @param mixed $cacheKey
	 * @return string
	 */
	private function doCachedExpansion( $frame, $input, $cacheKey ) {
		$hash = md5( serialize( $cacheKey ) );
		if ( isset( $this->expandCache[$hash] ) ) {
			return $this->expandCache[$hash];
		}

		if ( is_scalar( $input ) ) {
			$input = str_replace( [ "\r\n", "\r" ], "\n", $input );
			$dom = $this->parser->getPreprocessor()->preprocessToObj(
				$input, $frame->depth ? Parser::PTD_FOR_INCLUSION : 0 );
		} else {
			$dom = $input;
		}
		$ret = $frame->expand( $dom );
		if ( !$frame->isVolatile() ) {
			if ( count( $this->expandCache ) > self::MAX_EXPAND_CACHE_SIZE ) {
				reset( $this->expandCache );
				$oldHash = key( $this->expandCache );
				unset( $this->expandCache[$oldHash] );
			}
			$this->expandCache[$hash] = $ret;
		}
		return $ret;
	}
}
