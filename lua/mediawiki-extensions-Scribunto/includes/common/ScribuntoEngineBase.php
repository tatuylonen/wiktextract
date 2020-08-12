<?php

/**
 * Wikitext scripting infrastructure for MediaWiki: base classes.
 * Copyright (C) 2012 Victor Vasiliev <vasilvv@gmail.com> et al
 * https://www.mediawiki.org/
 *
 * This program is free software; you can redistribute it and/or modify
 * it under the terms of the GNU General Public License as published by
 * the Free Software Foundation; either version 2 of the License, or
 * (at your option) any later version.
 *
 * This program is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
 * GNU General Public License for more details.
 *
 * You should have received a copy of the GNU General Public License along
 * with this program; if not, write to the Free Software Foundation, Inc.,
 * 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA.
 * http://www.gnu.org/copyleft/gpl.html
 */

/**
 * Base class for all script engines. Includes all code
 * not related to particular modules, like tracking links between
 * modules or loading module texts.
 */
abstract class ScribuntoEngineBase {

	// Flags for ScribuntoEngineBase::getResourceUsage()
	const CPU_SECONDS = 1;
	const MEM_PEAK_BYTES = 2;

	/**
	 * @var Title|null
	 */
	protected $title;

	/**
	 * @var array
	 */
	protected $options;

	/**
	 * @var (ScribuntoModuleBase|null)[]
	 */
	protected $modules = [];

	/**
	 * @var Parser|null
	 */
	protected $parser;

	/**
	 * Creates a new module object within this engine
	 *
	 * @param string $text
	 * @param string|bool $chunkName
	 * @return ScribuntoModuleBase
	 */
	abstract protected function newModule( $text, $chunkName );

	/**
	 * Run an interactive console request
	 *
	 * @param array $params Associative array. Options are:
	 *    - title: The title object for the module being debugged
	 *    - content: The text content of the module
	 *    - prevQuestions: An array of previous "questions" used to establish the state
	 *    - question: The current "question", a string script
	 *
	 * @return array containing:
	 *    - print: The resulting print buffer
	 *    - return: The resulting return value
	 */
	abstract public function runConsole( array $params );

	/**
	 * Get software information for Special:Version
	 * @param array &$software
	 */
	abstract public function getSoftwareInfo( array &$software );

	/**
	 * @param array $options Associative array of options:
	 *    - parser:            A Parser object
	 */
	public function __construct( array $options ) {
		$this->options = $options;
		if ( isset( $options['parser'] ) ) {
			$this->parser = $options['parser'];
		}
		if ( isset( $options['title'] ) ) {
			$this->title = $options['title'];
		}
	}

	public function __destruct() {
		$this->destroy();
	}

	public function destroy() {
		// Break reference cycles
		$this->parser = null;
		$this->title = null;
		$this->modules = [];
	}

	/**
	 * @param Title $title
	 */
	public function setTitle( $title ) {
		$this->title = $title;
	}

	/**
	 * @return Title
	 */
	public function getTitle() {
		return $this->title;
	}

	/**
	 * Get an element from the configuration array
	 *
	 * @param string $optionName
	 * @return mixed
	 */
	public function getOption( $optionName ) {
		return $this->options[$optionName] ?? null;
	}

	/**
	 * @param string $message
	 * @param array $params
	 * @return ScribuntoException
	 */
	public function newException( $message, array $params = [] ) {
		return new ScribuntoException( $message, $this->getDefaultExceptionParams() + $params );
	}

	/**
	 * @return array
	 */
	public function getDefaultExceptionParams() {
		$params = [];
		if ( $this->title ) {
			$params['title'] = $this->title;
		}
		return $params;
	}

	/**
	 * Load a module from some parser-defined template loading mechanism and
	 * register a parser output dependency.
	 *
	 * Does not initialize the module, i.e. do not expect it to complain if the module
	 * text is garbage or has syntax error. Returns a module or null if it doesn't exist.
	 *
	 * @param Title $title The title of the module
	 * @return ScribuntoModuleBase|null
	 */
	public function fetchModuleFromParser( Title $title ) {
		$key = $title->getPrefixedDBkey();
		if ( !array_key_exists( $key, $this->modules ) ) {
			list( $text, $finalTitle ) = $this->parser->fetchTemplateAndTitle( $title );
			if ( $text === false ) {
				$this->modules[$key] = null;
				return null;
			}

			$finalKey = $finalTitle->getPrefixedDBkey();
			if ( !isset( $this->modules[$finalKey] ) ) {
				$this->modules[$finalKey] = $this->newModule( $text, $finalKey );
			}
			// Almost certainly $key === $finalKey, but just in case...
			$this->modules[$key] = $this->modules[$finalKey];
		}
		return $this->modules[$key];
	}

	/**
	 * Validates the script and returns a Status object containing the syntax
	 * errors for the given code.
	 *
	 * @param string $text
	 * @param string|bool $chunkName
	 * @return Status
	 */
	public function validate( $text, $chunkName = false ) {
		$module = $this->newModule( $text, $chunkName );
		return $module->validate();
	}

	/**
	 * Get CPU and memory usage information, if the script engine
	 * provides it.
	 *
	 * If the script engine is capable of reporting CPU and memory usage
	 * data, it should override this implementation.
	 *
	 * @param int $resource One of ScribuntoEngineBase::CPU_SECONDS
	 *  or ScribuntoEngineBase::MEM_PEAK_BYTES.
	 * @return float|int|false Resource usage for the specified resource
	 *  or false if not available.
	 */
	public function getResourceUsage( $resource ) {
		return false;
	}

	/**
	 * Get the language for GeSHi syntax highlighter.
	 * @return string|false
	 */
	public function getGeSHiLanguage() {
		return false;
	}

	/**
	 * Get the language for Ace code editor.
	 * @return string|false
	 */
	public function getCodeEditorLanguage() {
		return false;
	}

	/**
	 * @return Parser
	 */
	public function getParser() {
		return $this->parser;
	}

	/**
	 * Load a list of all libraries supported by this engine
	 *
	 * The return value is an array with keys being the library name seen by
	 * the module and values being either a PHP class name or an array with the
	 * following elements:
	 *  - class: (string) Class to load (required)
	 *  - deferLoad: (bool) Library should not be loaded at startup; modules
	 *      needing the library must request it (e.g. via 'require' in Lua)
	 *
	 * @param string $engine script engine we're using (eg: lua)
	 * @param array $coreLibraries Array of core libraries we support
	 * @return array
	 */
	protected function getLibraries( $engine, array $coreLibraries = [] ) {
		$extraLibraries = [];
		Hooks::run( 'ScribuntoExternalLibraries', [ $engine, &$extraLibraries ] );
		return $coreLibraries + $extraLibraries;
	}

	/**
	 * Load a list of all paths libraries can be in for this engine
	 *
	 * @param string $engine script engine we're using (eg: lua)
	 * @param array $coreLibraryPaths Array of library paths to use by default
	 * @return array
	 */
	protected function getLibraryPaths( $engine, array $coreLibraryPaths = [] ) {
		$extraLibraryPaths = [];
		Hooks::run( 'ScribuntoExternalLibraryPaths', [ $engine, &$extraLibraryPaths ] );
		return array_merge( $coreLibraryPaths, $extraLibraryPaths );
	}

	/**
	 * Add limit report data to a ParserOutput object
	 *
	 * @param ParserOutput $output ParserOutput object in which to add limit data
	 * @return null
	 */
	public function reportLimitData( ParserOutput $output ) {
	}

	/**
	 * Format limit report data
	 *
	 * @param string $key
	 * @param mixed &$value
	 * @param string &$report
	 * @param bool $isHTML
	 * @param bool $localize
	 * @return bool
	 */
	public function formatLimitData( $key, &$value, &$report, $isHTML, $localize ) {
		return true;
	}
}
