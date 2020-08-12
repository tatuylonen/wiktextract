<?php

class Scribunto_LuaCommonTestsFailLibrary extends Scribunto_LuaLibraryBase {
	public function __construct() {
		throw new MWException( 'deferLoad library that is never required was loaded anyway' );
	}

	public function register() {
	}
}
