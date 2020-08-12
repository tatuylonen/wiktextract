<?php

class Scribunto_LuaTextLibraryTest extends Scribunto_LuaEngineUnitTestBase {
	protected static $moduleName = 'TextLibraryTests';

	protected function setUp() : void {
		parent::setUp();

		// For unstrip test
		$parser = $this->getEngine()->getParser();
		$markers = [
			'nowiki' => Parser::MARKER_PREFIX . '-test-nowiki-' . Parser::MARKER_SUFFIX,
			'general' => Parser::MARKER_PREFIX . '-test-general-' . Parser::MARKER_SUFFIX,
		];
		$parser->mStripState->addNoWiki( $markers['nowiki'], 'NoWiki' );
		$parser->mStripState->addGeneral( $markers['general'], 'General' );
		$interpreter = $this->getEngine()->getInterpreter();
		$interpreter->callFunction(
			$interpreter->loadString( 'mw.text.stripTest = ...', 'fortest' ),
			$markers
		);
	}

	protected function getTestModules() {
		return parent::getTestModules() + [
			'TextLibraryTests' => __DIR__ . '/TextLibraryTests.lua',
		];
	}
}
