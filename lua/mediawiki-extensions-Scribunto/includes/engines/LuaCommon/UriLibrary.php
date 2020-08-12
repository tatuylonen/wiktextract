<?php

class Scribunto_LuaUriLibrary extends Scribunto_LuaLibraryBase {
	public function register() {
		$lib = [
			'anchorEncode' => [ $this, 'anchorEncode' ],
			'localUrl' => [ $this, 'localUrl' ],
			'fullUrl' => [ $this, 'fullUrl' ],
			'canonicalUrl' => [ $this, 'canonicalUrl' ],
		];

		return $this->getEngine()->registerInterface( 'mw.uri.lua', $lib, [
			'defaultUrl' => $this->getTitle()->getFullUrl(),
		] );
	}

	/**
	 * Handler for anchorEncode
	 * @internal
	 * @param string $s
	 * @return string[]
	 */
	public function anchorEncode( $s ) {
		return [ CoreParserFunctions::anchorencode(
			$this->getParser(), $s
		) ];
	}

	/**
	 * Get a URL (helper for handlers)
	 * @param string $func Title class method to call
	 * @param string $page Page title
	 * @param array $query Query string
	 * @return string[]|null[]
	 */
	private function getUrl( $func, $page, $query ) {
		$title = Title::newFromText( $page );
		if ( !$title ) {
			$title = Title::newFromURL( urldecode( $page ) );
		}
		if ( $title ) {
			# Convert NS_MEDIA -> NS_FILE
			if ( $title->getNamespace() == NS_MEDIA ) {
				$title = Title::makeTitle( NS_FILE, $title->getDBkey() );
			}
			if ( $query !== null ) {
				$text = $title->$func( $query );
			} else {
				$text = $title->$func();
			}
			return [ $text ];
		} else {
			return [ null ];
		}
	}

	/**
	 * Handler for localUrl
	 * @internal
	 * @param string $page
	 * @param array $query
	 * @return string[]|null[]
	 */
	public function localUrl( $page, $query ) {
		return $this->getUrl( 'getLocalURL', $page, $query );
	}

	/**
	 * Handler for fullUrl
	 * @internal
	 * @param string $page
	 * @param array $query
	 * @return string[]|null[]
	 */
	public function fullUrl( $page, $query ) {
		return $this->getUrl( 'getFullURL', $page, $query );
	}

	/**
	 * Handler for canonicalUrl
	 * @internal
	 * @param string $page
	 * @param array $query
	 * @return string[]|null[]
	 */
	public function canonicalUrl( $page, $query ) {
		return $this->getUrl( 'getCanonicalURL', $page, $query );
	}
}
