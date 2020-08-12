<?php

use Wikimedia\ScopedCallback;

/**
 * @covers Scribunto_LuaUstringLibrary
 */
class Scribunto_LuaUstringLibraryTest extends Scribunto_LuaEngineUnitTestBase {
	protected static $moduleName = 'UstringLibraryTests';

	private $normalizationDataProvider = null;

	protected function tearDown() : void {
		if ( $this->normalizationDataProvider ) {
			$this->normalizationDataProvider->destroy();
			$this->normalizationDataProvider = null;
		}
		parent::tearDown();
	}

	protected function getTestModules() {
		return parent::getTestModules() + [
			'UstringLibraryTests' => __DIR__ . '/UstringLibraryTests.lua',
			'UstringLibraryNormalizationTests' => __DIR__ . '/UstringLibraryNormalizationTests.lua',
		];
	}

	public function testUstringLibraryNormalizationTestsAvailable() {
		if ( UstringLibraryNormalizationTestProvider::available( $err ) ) {
			$this->assertTrue( true );
		} else {
			$this->markTestSkipped( $err );
		}
	}

	public function provideUstringLibraryNormalizationTests() {
		if ( !$this->normalizationDataProvider ) {
			$this->normalizationDataProvider =
				new UstringLibraryNormalizationTestProvider( $this->getEngine() );
		}
		return $this->normalizationDataProvider;
	}

	/**
	 * @dataProvider provideUstringLibraryNormalizationTests
	 */
	public function testUstringLibraryNormalizationTests( $name, $c1, $c2, $c3, $c4, $c5 ) {
		$this->luaTestName = "UstringLibraryNormalization: $name";
		$dataProvider = $this->provideUstringLibraryNormalizationTests();
		$expected = [
			$c2, $c2, $c2, $c4, $c4, // NFC
			$c3, $c3, $c3, $c5, $c5, // NFD
			$c4, $c4, $c4, $c4, $c4, // NFKC
			$c5, $c5, $c5, $c5, $c5, // NFKD
		];
		foreach ( $expected as &$e ) {
			$chars = array_values( unpack( 'N*', mb_convert_encoding( $e, 'UTF-32BE', 'UTF-8' ) ) );
			foreach ( $chars as &$c ) {
				$c = sprintf( "%x", $c );
			}
			$e = "$e\t" . implode( "\t", $chars );
		}
		$actual = $dataProvider->runNorm( $c1, $c2, $c3, $c4, $c5 );
		$this->assertSame( $expected, $actual );
		$this->luaTestName = null;
	}

	/**
	 * @dataProvider providePCREErrors
	 */
	public function testPCREErrors( $ini, $args, $error ) {
		$reset = [];
		foreach ( $ini as $key => $value ) {
			$old = ini_set( $key, $value );
			if ( $old === false ) {
				$this->markTestSkipped( "Failed to set ini setting $key = $value" );
			}
			$reset[] = new ScopedCallback( 'ini_set', [ $key, $old ] );
		}

		$interpreter = $this->getEngine()->getInterpreter();
		$func = $interpreter->loadString( 'return mw.ustring.gsub( ... )', 'fortest' );
		try {
			$interpreter->callFunction( $func, ...$args );
			$this->fail( 'Expected exception not thrown' );
		} catch ( Scribunto_LuaError $e ) {
			$this->assertSame( $error, $e->getMessage() );
		}
	}

	public static function providePCREErrors() {
		return [
			[
				[ 'pcre.backtrack_limit' => 10 ],
				[ 'zzzzzzzzzzzzzzzzzzzz', '^(.-)[abc]*$', '%1' ],
				'Lua error: PCRE backtrack limit reached while matching pattern \'^(.-)[abc]*$\'.'
			],
			// @TODO: Figure out patterns that hit other PCRE limits
		];
	}
}
