<?php

class Scribunto_LuaHashLibraryTest extends Scribunto_LuaEngineUnitTestBase {
	protected static $moduleName = 'HashLibraryTests';

	protected function getTestModules() {
		return parent::getTestModules() + [
			'HashLibraryTests' => __DIR__ . '/HashLibraryTests.lua',
		];
	}

}
