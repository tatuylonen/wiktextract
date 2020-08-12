<?php

use UtfNormal\Validator;

class Scribunto_LuaError extends ScribuntoException {
	public $luaMessage;

	/**
	 * @param string $message
	 * @param array $options
	 */
	public function __construct( $message, array $options = [] ) {
		$this->luaMessage = $message;
		$options = $options + [ 'args' => [ Validator::cleanUp( $message ) ] ];
		if ( isset( $options['module'] ) && isset( $options['line'] ) ) {
			$msg = 'scribunto-lua-error-location';
		} else {
			$msg = 'scribunto-lua-error';
		}

		parent::__construct( $msg, $options );
	}

	/**
	 * @return string
	 */
	public function getLuaMessage() {
		return $this->luaMessage;
	}

	/**
	 * @param array $options Options for message processing. Currently supports:
	 * $options['msgOptions']['content'] to use content language.
	 * @return bool|string
	 */
	public function getScriptTraceHtml( $options = [] ) {
		if ( !isset( $this->params['trace'] ) ) {
			return false;
		}
		if ( isset( $options['msgOptions'] ) ) {
			$msgOptions = $options['msgOptions'];
		} else {
			$msgOptions = [];
		}

		$s = '<ol class="scribunto-trace">';
		foreach ( $this->params['trace'] as $info ) {
			$short_src = $srcdefined = $info['short_src'];
			$currentline = $info['currentline'];

			$src = htmlspecialchars( $short_src );
			if ( $currentline > 0 ) {
				$src .= ':' . htmlspecialchars( $currentline );

				$title = Title::newFromText( $short_src );
				if ( $title && $title->hasContentModel( CONTENT_MODEL_SCRIBUNTO ) ) {
					$title = $title->createFragmentTarget( 'mw-ce-l' . $currentline );
					$src = Html::rawElement( 'a',
						[ 'href' => $title->getFullURL( 'action=edit' ) ],
						$src );
				}
			}

			if ( strval( $info['namewhat'] ) !== '' ) {
				$functionMsg = wfMessage( 'scribunto-lua-in-function', wfEscapeWikiText( $info['name'] ) );
				in_array( 'content', $msgOptions ) ?
					$function = $functionMsg->inContentLanguage()->plain() :
					$function = $functionMsg->plain();
			} elseif ( $info['what'] == 'main' ) {
				$functionMsg = wfMessage( 'scribunto-lua-in-main' );
				in_array( 'content', $msgOptions ) ?
					$function = $functionMsg->inContentLanguage()->plain() :
					$function = $functionMsg->plain();
			} else {
				// C function, tail call, or a Lua function where Lua can't
				// guess the name
				$function = '?';
			}

			$backtraceLineMsg = wfMessage( 'scribunto-lua-backtrace-line' )
				->rawParams( "<strong>$src</strong>" )
				->params( $function );
			in_array( 'content', $msgOptions ) ?
				$backtraceLine = $backtraceLineMsg->inContentLanguage()->parse() :
				$backtraceLine = $backtraceLineMsg->parse();

			$s .= "<li>$backtraceLine</li>";
		}
		$s .= '</ol>';
		return $s;
	}
}
