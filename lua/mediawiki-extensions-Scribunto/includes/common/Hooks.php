<?php
/**
 * Wikitext scripting infrastructure for MediaWiki: hooks.
 * Copyright (C) 2009-2012 Victor Vasiliev <vasilvv@gmail.com>
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

use MediaWiki\MediaWikiServices;
use UtfNormal\Validator;
use Wikimedia\PSquare;

/**
 * Hooks for the Scribunto extension.
 */
class ScribuntoHooks {

	/**
	 * Define content handler constant upon extension registration
	 */
	public static function onRegistration() {
		define( 'CONTENT_MODEL_SCRIBUNTO', 'Scribunto' );
	}

	/**
	 * Get software information for Special:Version
	 *
	 * @param array &$software
	 * @return bool
	 */
	public static function getSoftwareInfo( array &$software ) {
		$engine = Scribunto::newDefaultEngine();
		$engine->setTitle( Title::makeTitle( NS_SPECIAL, 'Version' ) );
		$engine->getSoftwareInfo( $software );
		return true;
	}

	/**
	 * Register parser hooks.
	 *
	 * @param Parser $parser
	 * @return bool
	 */
	public static function setupParserHook( Parser $parser ) {
		$parser->setFunctionHook( 'invoke', 'ScribuntoHooks::invokeHook', Parser::SFH_OBJECT_ARGS );
		return true;
	}

	/**
	 * Called when the interpreter is to be reset.
	 *
	 * @param Parser $parser
	 * @return bool
	 */
	public static function clearState( Parser $parser ) {
		Scribunto::resetParserEngine( $parser );
		return true;
	}

	/**
	 * Called when the parser is cloned
	 *
	 * @param Parser $parser
	 * @return bool
	 */
	public static function parserCloned( Parser $parser ) {
		$parser->scribunto_engine = null;
		return true;
	}

	/**
	 * Hook function for {{#invoke:module|func}}
	 *
	 * @param Parser $parser
	 * @param PPFrame $frame
	 * @param array $args
	 * @throws MWException
	 * @throws ScribuntoException
	 * @return string
	 */
	public static function invokeHook( Parser $parser, PPFrame $frame, array $args ) {
		global $wgScribuntoGatherFunctionStats;

		try {
			if ( count( $args ) < 2 ) {
				throw new ScribuntoException( 'scribunto-common-nofunction' );
			}
			$moduleName = trim( $frame->expand( $args[0] ) );
			$engine = Scribunto::getParserEngine( $parser );

			$title = Title::makeTitleSafe( NS_MODULE, $moduleName );
			if ( !$title || !$title->hasContentModel( CONTENT_MODEL_SCRIBUNTO ) ) {
				throw new ScribuntoException( 'scribunto-common-nosuchmodule',
					[ 'args' => [ $moduleName ] ] );
			}
			$module = $engine->fetchModuleFromParser( $title );
			if ( !$module ) {
				throw new ScribuntoException( 'scribunto-common-nosuchmodule',
					[ 'args' => [ $moduleName ] ] );
			}
			$functionName = trim( $frame->expand( $args[1] ) );

			$bits = $args[1]->splitArg();
			unset( $args[0] );
			unset( $args[1] );

			// If $bits['index'] is empty, then the function name was parsed as a
			// key=value pair (because of an equals sign in it), and since it didn't
			// have an index, we don't need the index offset.
			$childFrame = $frame->newChild( $args, $title, $bits['index'] === '' ? 0 : 1 );

			if ( $wgScribuntoGatherFunctionStats ) {
				$u0 = $engine->getResourceUsage( $engine::CPU_SECONDS );
				$result = $module->invoke( $functionName, $childFrame );
				$u1 = $engine->getResourceUsage( $engine::CPU_SECONDS );

				if ( $u1 > $u0 ) {
					$timingMs = (int)( 1000 * ( $u1 - $u0 ) );
					// Since the overhead of stats is worst when when #invoke
					// calls are very short, don't process measurements <= 20ms.
					if ( $timingMs > 20 ) {
						self::reportTiming( $moduleName, $functionName, $timingMs );
					}
				}
			} else {
				$result = $module->invoke( $functionName, $childFrame );
			}

			return Validator::cleanUp( strval( $result ) );
		} catch ( ScribuntoException $e ) {
			$trace = $e->getScriptTraceHtml( [ 'msgOptions' => [ 'content' ] ] );
			$html = Html::element( 'p', [], $e->getMessage() );
			if ( $trace !== false ) {
				$html .= Html::element( 'p',
					[],
					wfMessage( 'scribunto-common-backtrace' )->inContentLanguage()->text()
				) . $trace;
			} else {
				$html .= Html::element( 'p',
					[],
					wfMessage( 'scribunto-common-no-details' )->inContentLanguage()->text()
				);
			}
			$out = $parser->getOutput();
			$errors = $out->getExtensionData( 'ScribuntoErrors' );
			if ( $errors === null ) {
				// On first hook use, set up error array and output
				$errors = [];
				$parser->addTrackingCategory( 'scribunto-common-error-category' );
				$out->addModules( 'ext.scribunto.errors' );
			}
			$errors[] = $html;
			$out->setExtensionData( 'ScribuntoErrors', $errors );
			$out->addJsConfigVars( 'ScribuntoErrors', $errors );
			$id = 'mw-scribunto-error-' . ( count( $errors ) - 1 );
			$parserError = htmlspecialchars( $e->getMessage() );

			// #iferror-compatible error element
			return "<strong class=\"error\"><span class=\"scribunto-error\" id=\"$id\">" .
				$parserError . "</span></strong>";
		}
	}

	/**
	 * Record stats on slow function calls.
	 *
	 * @param string $moduleName
	 * @param string $functionName
	 * @param int $timing Function execution time in milliseconds.
	 */
	public static function reportTiming( $moduleName, $functionName, $timing ) {
		global $wgScribuntoGatherFunctionStats, $wgScribuntoSlowFunctionThreshold;

		if ( !$wgScribuntoGatherFunctionStats ) {
			return;
		}

		$threshold = $wgScribuntoSlowFunctionThreshold;
		if ( !( is_float( $threshold ) && $threshold > 0 && $threshold < 1 ) ) {
			return;
		}

		static $cache;

		if ( !$cache ) {
			$cache = ObjectCache::getLocalServerInstance( CACHE_NONE );

		}

		// To control the sampling rate, we keep a compact histogram of
		// observations in APC, and extract the Nth percentile (specified
		// via $wgScribuntoSlowFunctionThreshold; defaults to 0.90).
		// We need APC and \Wikimedia\PSquare to do that.
		if ( !class_exists( PSquare::class ) || $cache instanceof EmptyBagOStuff ) {
			return;
		}

		$cacheVersion = '1';
		$key = $cache->makeGlobalKey( __METHOD__, $cacheVersion, (string)$threshold );

		// This is a classic "read-update-write" critical section with no
		// mutual exclusion, but the only consequence is that some samples
		// will be dropped. We only need enough samples to estimate the
		// the shape of the data, so that's fine.
		$ps = $cache->get( $key ) ?: new PSquare( $threshold );
		$ps->addObservation( $timing );
		$cache->set( $key, $ps, 60 );

		if ( $ps->getCount() < 1000 || $timing < $ps->getValue() ) {
			return;
		}

		static $stats;

		if ( !$stats ) {
			$stats = MediaWikiServices::getInstance()->getStatsdDataFactory();
		}

		$metricKey = sprintf( 'scribunto.traces.%s__%s__%s', wfWikiId(), $moduleName, $functionName );
		$stats->timing( $metricKey, $timing );
	}

	/**
	 * @param Title $title
	 * @param string &$languageCode
	 * @return bool
	 */
	public static function getCodeLanguage( Title $title, &$languageCode ) {
		global $wgScribuntoUseCodeEditor;
		if ( $wgScribuntoUseCodeEditor && $title->hasContentModel( CONTENT_MODEL_SCRIBUNTO )
		) {
			$engine = Scribunto::newDefaultEngine();
			if ( $engine->getCodeEditorLanguage() ) {
				$languageCode = $engine->getCodeEditorLanguage();
				return false;
			}
		}

		return true;
	}

	/**
	 * Set the Scribunto content handler for modules
	 *
	 * @param Title $title
	 * @param string &$model
	 * @return bool
	 */
	public static function contentHandlerDefaultModelFor( Title $title, &$model ) {
		if ( $model === 'sanitized-css' ) {
			// Let TemplateStyles override Scribunto
			return true;
		}
		if ( $title->getNamespace() == NS_MODULE && !Scribunto::isDocPage( $title ) ) {
			$model = CONTENT_MODEL_SCRIBUNTO;
			return true;
		}
		return true;
	}

	/**
	 * Adds report of number of evaluations by the single wikitext page.
	 *
	 * @param Parser $parser
	 * @param ParserOutput $output
	 * @return bool
	 */
	public static function reportLimitData( Parser $parser, ParserOutput $output ) {
		if ( Scribunto::isParserEnginePresent( $parser ) ) {
			$engine = Scribunto::getParserEngine( $parser );
			$engine->reportLimitData( $output );
		}
		return true;
	}

	/**
	 * Formats the limit report data
	 *
	 * @param string $key
	 * @param mixed &$value
	 * @param string &$report
	 * @param bool $isHTML
	 * @param bool $localize
	 * @return bool
	 */
	public static function formatLimitData( $key, &$value, &$report, $isHTML, $localize ) {
		$engine = Scribunto::newDefaultEngine();
		return $engine->formatLimitData( $key, $value, $report, $isHTML, $localize );
	}

	/**
	 * EditPage::showStandardInputs:options hook
	 *
	 * @param EditPage $editor
	 * @param OutputPage $output
	 * @param int &$tab Current tabindex
	 * @return bool
	 */
	public static function showStandardInputsOptions( EditPage $editor, OutputPage $output, &$tab ) {
		if ( $editor->getTitle()->hasContentModel( CONTENT_MODEL_SCRIBUNTO ) ) {
			$output->addModules( 'ext.scribunto.edit' );
			$editor->editFormTextAfterTools .= '<div id="mw-scribunto-console"></div>';
		}
		return true;
	}

	/**
	 * EditPage::showReadOnlyForm:initial hook
	 *
	 * @param EditPage $editor
	 * @param OutputPage $output
	 * @return bool
	 */
	public static function showReadOnlyFormInitial( EditPage $editor, OutputPage $output ) {
		if ( $editor->getTitle()->hasContentModel( CONTENT_MODEL_SCRIBUNTO ) ) {
			$output->addModules( 'ext.scribunto.edit' );
			$editor->editFormTextAfterContent .= '<div id="mw-scribunto-console"></div>';
		}
		return true;
	}

	/**
	 * EditPageBeforeEditButtons hook
	 *
	 * @param EditPage $editor
	 * @param array &$buttons Button array
	 * @param int &$tabindex Current tabindex
	 * @return bool
	 */
	public static function beforeEditButtons( EditPage $editor, array &$buttons, &$tabindex ) {
		if ( $editor->getTitle()->hasContentModel( CONTENT_MODEL_SCRIBUNTO ) ) {
			unset( $buttons['preview'] );
		}
		return true;
	}

	/**
	 * @param IContextSource $context
	 * @param Content $content
	 * @param Status $status
	 * @return bool
	 */
	public static function validateScript( IContextSource $context, Content $content,
		Status $status
	) {
		$title = $context->getTitle();

		if ( !$content instanceof ScribuntoContent ) {
			return true;
		}

		$validateStatus = $content->validate( $title );
		if ( $validateStatus->isOK() ) {
			return true;
		}

		$status->merge( $validateStatus );

		if ( isset( $validateStatus->scribunto_error->params['module'] ) ) {
			$module = $validateStatus->scribunto_error->params['module'];
			$line = $validateStatus->scribunto_error->params['line'];
			if ( $module === $title->getPrefixedDBkey() && preg_match( '/^\d+$/', $line ) ) {
				$out = $context->getOutput();
				$out->addInlineScript( 'window.location.hash = ' . Xml::encodeJsVar( "#mw-ce-l$line" ) );
			}
		}

		return true;
	}

	/**
	 * @param Article $article
	 * @param bool &$outputDone
	 * @param bool &$pcache
	 * @return bool
	 */
	public static function showDocPageHeader( Article $article, &$outputDone, &$pcache ) {
		$title = $article->getTitle();
		if ( Scribunto::isDocPage( $title, $forModule ) ) {
			$article->getContext()->getOutput()->addHTML(
				wfMessage( 'scribunto-doc-page-header', $forModule->getPrefixedText() )->parseAsBlock()
			);
		}
		return true;
	}
}
