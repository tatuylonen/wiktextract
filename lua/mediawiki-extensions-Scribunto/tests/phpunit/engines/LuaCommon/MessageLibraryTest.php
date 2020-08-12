<?php

class Scribunto_LuaMessageLibraryTest extends Scribunto_LuaEngineUnitTestBase {
	protected static $moduleName = 'MessageLibraryTests';

	protected function getTestModules() {
		return parent::getTestModules() + [
			'MessageLibraryTests' => __DIR__ . '/MessageLibraryTests.lua',
		];
	}
}
