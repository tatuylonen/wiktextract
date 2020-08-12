<?php

class Scribunto_LuaSiteLibraryTest extends Scribunto_LuaEngineUnitTestBase {
	protected static $moduleName = 'SiteLibraryTests';

	protected function getTestModules() {
		return parent::getTestModules() + [
			'SiteLibraryTests' => __DIR__ . '/SiteLibraryTests.lua',
		];
	}
}
