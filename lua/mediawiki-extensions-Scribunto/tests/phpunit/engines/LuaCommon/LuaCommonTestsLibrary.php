<?php

class Scribunto_LuaCommonTestsLibrary extends Scribunto_LuaLibraryBase {
	public function register() {
		$lib = [
			'test' => [ $this, 'test' ],
		];
		$opts = [
			'test' => 'Test option',
		];

		return $this->getEngine()->registerInterface( __DIR__ . '/CommonTests-lib.lua', $lib, $opts );
	}

	public function test() {
		return [ 'Test function' ];
	}
}
