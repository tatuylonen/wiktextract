<?php

class Scribunto_LuaLibraryUtilTest extends Scribunto_LuaEngineUnitTestBase {
	protected static $moduleName = 'LibraryUtilTests';

	protected function getTestModules() {
		return parent::getTestModules() + [
			'LibraryUtilTests' => __DIR__ . '/LibraryUtilTests.lua',
		];
	}
}
