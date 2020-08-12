<?php

class Scribunto_LuaHtmlLibrary extends Scribunto_LuaLibraryBase {
	public function register() {
		return $this->getEngine()->registerInterface( 'mw.html.lua', [], [
			'uniqPrefix' => Parser::MARKER_PREFIX,
			'uniqSuffix' => Parser::MARKER_SUFFIX,
		] );
	}
}
