/* eslint-disable no-use-before-define */

( function () {

	/**
	 * Debug console
	 * Based on JavaScript Shell 1.4 by Jesse Ruderman (GPL/LGPL/MPL tri-license)
	 *
	 * TODO:
	 *    * Refactor, more jQuery, etc.
	 *    * Spinner?
	 *    * A prompt in front of input lines and the textarea
	 *    * Collapsible backtrace display
	 */

	var histList = [ '' ],
		histPos = 0,
		question,
		input,
		output,
		$spinner,
		sessionContent = null,
		sessionKey = null,
		pending = false,
		clearNextRequest = false;

	function refocus() {
		// Needed for Mozilla to scroll correctly
		input.blur();
		input.focus();
	}

	function initConsole() {
		input = document.getElementById( 'mw-scribunto-input' );
		output = document.getElementById( 'mw-scribunto-output' );
		$spinner = $.createSpinner( { size: 'small', type: 'block' } );

		recalculateInputHeight();
		println( mw.msg( 'scribunto-console-intro' ), 'mw-scribunto-message' );
	}

	/**
	 * Use onkeydown because IE doesn't support onkeypress for arrow keys
	 *
	 * @param {jQuery.Event} e
	 */
	function inputKeydown( e ) {
		if ( e.shiftKey && e.keyCode === 13 ) {
			// shift-enter
			// don't do anything; allow the shift-enter to insert a line break as normal
		} else if ( e.keyCode === 13 ) {
			// enter
			// execute the input on enter
			go();
		} else if ( e.keyCode === 38 ) {
			// up
			// go up in history if at top or ctrl-up
			if ( e.ctrlKey || caretInFirstLine( input ) ) {
				hist( 'up' );
			}
		} else if ( e.keyCode === 40 ) {
			// down
			// go down in history if at end or ctrl-down
			if ( e.ctrlKey || caretInLastLine( input ) ) {
				hist( 'down' );
			}
		}

		setTimeout( recalculateInputHeight, 0 );
	}

	function inputFocus() {
		if ( sessionContent === null ) {
			// No previous state to clear
			return;
		}

		if ( clearNextRequest ) {
			// User already knows
			return;
		}

		if ( getContent() !== sessionContent ) {
			printClearBar( 'scribunto-console-cleared' );
			clearNextRequest = true;
		}
	}

	function caretInFirstLine( textbox ) {
		var firstLineBreak;

		// IE doesn't support selectionStart/selectionEnd
		if ( textbox.selectionStart === undefined ) {
			return true;
		}

		firstLineBreak = textbox.value.indexOf( '\n' );

		return ( ( firstLineBreak === -1 ) || ( textbox.selectionStart <= firstLineBreak ) );
	}

	function caretInLastLine( textbox ) {
		var lastLineBreak;

		// IE doesn't support selectionStart/selectionEnd
		if ( textbox.selectionEnd === undefined ) {
			return true;
		}

		lastLineBreak = textbox.value.lastIndexOf( '\n' );

		return ( textbox.selectionEnd > lastLineBreak );
	}

	function recalculateInputHeight() {
		var rows = input.value.split( /\n/ ).length +
			// prevent scrollbar flickering in Mozilla
			1 +
			// leave room for scrollbar in Opera
			( window.opera ? 1 : 0 );

		// without this check, it is impossible to select text in Opera 7.60 or Opera 8.0.
		if ( input.rows !== rows ) {
			input.rows = rows;
		}
	}

	function println( s, type ) {
		var newdiv;
		if ( ( s = String( s ) ) ) {
			newdiv = document.createElement( 'div' );
			newdiv.appendChild( document.createTextNode( s ) );
			newdiv.className = type;
			output.appendChild( newdiv );
			return newdiv;
		}
	}

	function printClearBar( msg ) {
		$( '<div>' )
			.attr( 'class', 'mw-scribunto-clear' )
			.text( mw.msg( msg ) )
			.appendTo( output );
	}

	function hist( direction ) {
		// histList[0] = first command entered, [1] = second, etc.
		// type something, press up --> thing typed is now in "limbo"
		// (last item in histList) and should be reachable by pressing
		// down again.

		var L = histList.length;

		if ( L === 1 ) {
			return;
		}

		if ( direction === 'up' ) {
			if ( histPos === L - 1 ) {
				// Save this entry in case the user hits the down key.
				histList[ histPos ] = input.value;
			}

			if ( histPos > 0 ) {
				histPos--;
				// Use a timeout to prevent up from moving cursor within new text
				// Set to nothing first for the same reason
				setTimeout(
					function () {
						var caretPos;
						input.value = '';
						input.value = histList[ histPos ];
						caretPos = input.value.length;
						if ( input.setSelectionRange ) {
							input.setSelectionRange( caretPos, caretPos );
						}
					},
					0
				);
			}
		} else {
			// direction down
			if ( histPos < L - 1 ) {
				histPos++;
				input.value = histList[ histPos ];
			} else if ( histPos === L - 1 ) {
				// Already on the current entry: clear but save
				if ( input.value ) {
					histList[ histPos ] = input.value;
					++histPos;
					input.value = '';
				}
			}
		}
	}

	function printQuestion( q ) {
		println( q, 'mw-scribunto-input' );
	}

	function printError( er ) {
		var lineNumberString;

		if ( er.name ) {
			// lineNumberString should not be '', to avoid a very wacky bug in IE 6.
			lineNumberString = ( er.lineNumber !== undefined ) ? ( ' on line ' + er.lineNumber + ': ' ) : ': ';
			// Because IE doesn't have error.toString.
			println( er.name + lineNumberString + er.message, 'mw-scribunto-error' );
		} else {
			// Because security errors in Moz /only/ have toString.
			println( er, 'mw-scribunto-error' );
		}
	}

	function setPending() {
		pending = true;
		input.readOnly = true;
		$spinner.insertBefore( input );
	}

	function clearPending() {
		$spinner.remove();
		pending = false;
		input.readOnly = false;
	}

	function go() {
		var params, api, content, sentContent;

		if ( pending ) {
			// If there is an XHR request pending, don't send another one
			// We set readOnly on the textarea to give a UI indication, this is
			// just for paranoia.
			return;
		}

		question = input.value;

		if ( question === '' ) {
			return;
		}

		histList[ histList.length - 1 ] = question;
		histList[ histList.length ] = '';
		histPos = histList.length - 1;

		// Unfortunately, this has to happen *before* the script is run, so that
		// print() output will go in the right place.
		input.value = '';
		// can't preventDefault on input, so also clear it later
		setTimeout( function () {
			input.value = '';
		}, 0 );

		recalculateInputHeight();
		printQuestion( question );

		params = {
			action: 'scribunto-console',
			title: mw.config.get( 'wgPageName' ),
			question: question
		};

		content = getContent();
		sentContent = false;

		if ( !sessionKey || sessionContent !== content ) {
			params.clear = true;
			params.content = content;
			sentContent = true;
		}
		if ( sessionKey ) {
			params.session = sessionKey;
		}
		if ( clearNextRequest ) {
			params.clear = true;
			clearNextRequest = false;
		}

		api = new mw.Api();
		setPending();

		api.post( params )
			.done( function ( result ) {
				if ( result.sessionIsNew === '' && !sentContent ) {
					// Session was lost. Resend query, with content
					printClearBar( 'scribunto-console-cleared-session-lost' );
					sessionContent = null;
					clearPending();
					input.value = params.question;
					go();
					return;
				}
				sessionKey = result.session;
				sessionContent = content;
				if ( result.type === 'error' ) {
					$( '<div>' ).addClass( 'mw-scribunto-error' ).html( result.html ).appendTo( output );
				} else {
					if ( result.print !== '' ) {
						println( result.print, 'mw-scribunto-print' );
					}
					if ( result.return !== '' ) {
						println( result.return, 'mw-scribunto-normalOutput' );
					}
				}
				clearPending();
				setTimeout( refocus, 0 );
			} )
			.fail( function ( code, result ) {
				if ( result.error && result.error.info ) {
					printError( result.error.info );
				} else if ( result.exception ) {
					printError( 'Error sending API request: ' + result.exception );
				} else {
					mw.log( result );
					printError( 'error' );
				}
				clearPending();
				setTimeout( refocus, 0 );
			} );
	}

	function getContent() {
		var $textarea = $( '#wpTextbox1' ),
			context = $textarea.data( 'wikiEditor-context' );

		if ( context === undefined || context.codeEditor === undefined ) {
			return $textarea.val();
		} else {
			return $textarea.textSelection( 'getContents' );
		}
	}

	function onClearClick() {
		$( '#mw-scribunto-output' ).empty();
		clearNextRequest = true;
		refocus();
	}

	function initEditPage() {
		var $wpTextbox1,
			$console = $( '#mw-scribunto-console' );
		if ( !$console.length ) {
			// There is no console in the DOM; on read-only (protected) pages,
			// we need to add it here, because the hook does not insert
			// it server-side.
			$wpTextbox1 = $( '#wpTextbox1' );
			if ( !$wpTextbox1.length || !$wpTextbox1.prop( 'readonly' ) ) {
				return;
			}

			$console = $( '<div>' ).attr( { id: 'mw-scribunto-console' } );
			$wpTextbox1.after( $console );
		}

		$( '<fieldset>' )
			.attr( 'class', 'mw-scribunto-console-fieldset' )
			.append( $( '<legend>' ).text( mw.msg( 'scribunto-console-title' ) ) )
			.append( $( '<div id="mw-scribunto-output"></div>' ) )
			.append(
				$( '<div>' ).append(
					$( '<textarea>' )
						.attr( {
							id: 'mw-scribunto-input',
							class: 'mw-scribunto-input',
							wrap: 'off',
							rows: 1,
							dir: 'ltr',
							lang: 'en'
						} )
						.bind( 'keydown', inputKeydown )
						.bind( 'focus', inputFocus )
				)
			)
			.append(
				$( '<div>' ).append(
					$( '<input>' )
						.attr( {
							type: 'button',
							value: mw.msg( 'scribunto-console-clear' )
						} )
						.bind( 'click', onClearClick )
				)
			)
			.wrap( '<form>' )
			.appendTo( $console );

		initConsole();
	}

	$( function () {
		var action = mw.config.get( 'wgAction' );
		if ( action === 'edit' || action === 'submit' || action === 'editredlink' ) {
			initEditPage();
		}
	} );

}() );
