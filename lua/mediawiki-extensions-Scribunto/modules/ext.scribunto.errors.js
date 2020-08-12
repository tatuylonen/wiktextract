( function () {

	mw.hook( 'wikipage.content' ).add( function () {
		var errors = mw.config.get( 'ScribuntoErrors' ),
			regex = /^mw-scribunto-error-(\d+)/,
			$dialog = $( '<div>' );

		if ( !errors ) {
			mw.log( 'mw.scribunto.errors: ScribuntoErrors does not exist in mw.config' );
			errors = [];
		}

		$dialog.dialog( {
			title: mw.msg( 'scribunto-parser-dialog-title' ),
			autoOpen: false
		} );

		$( '.scribunto-error' ).each( function ( index, span ) {
			var errorId,
				matches = regex.exec( span.id );
			if ( matches === null ) {
				mw.log( 'mw.scribunto.errors: regex mismatch!' );
				return;
			}
			errorId = parseInt( matches[ 1 ], 10 );
			$( span ).on( 'click', function ( e ) {
				var error = errors[ errorId ];
				if ( typeof error !== 'string' ) {
					mw.log( 'mw.scribunto.errors: error ' + matches[ 1 ] + ' not found.' );
					return;
				}
				$dialog
					.dialog( 'close' )
					.html( error )
					.dialog( 'option', 'position', [ e.clientX + 5, e.clientY + 5 ] )
					.dialog( 'open' );
			} );
		} );
	} );

}() );
