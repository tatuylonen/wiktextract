<?php

if ( !wfIsCLI() ) {
	exit;
}

require_once __DIR__ . '/../LuaCommon/LuaInterpreterTest.php';

use Wikimedia\TestingAccessWrapper;

/**
 * @group Lua
 * @group LuaStandalone
 * @covers Scribunto_LuaStandaloneInterpreter
 */
class Scribunto_LuaStandaloneInterpreterTest extends Scribunto_LuaInterpreterTest {
	public $stdOpts = [
		'errorFile' => null,
		'luaPath' => null,
		'memoryLimit' => 50000000,
		'cpuLimit' => 30,
	];

	private function getVsize( $pid ) {
		$size = wfShellExec( wfEscapeShellArg( 'ps', '-p', $pid, '-o', 'vsz', '--no-headers' ) );
		return trim( $size ) * 1024;
	}

	protected function newInterpreter( $opts = [] ) {
		$opts = $opts + $this->stdOpts;
		$engine = new Scribunto_LuaStandaloneEngine( $this->stdOpts );
		return new Scribunto_LuaStandaloneInterpreter( $engine, $opts );
	}

	public function testIOErrorExit() {
		$interpreter = $this->newInterpreter();
		try {
			$interpreter->testquit();
			$this->fail( 'Expected exception not thrown' );
		} catch ( ScribuntoException $ex ) {
			$this->assertSame( 'scribunto-luastandalone-exited', $ex->getMessageName() );
			$this->assertSame( [ '[UNKNOWN]', 42 ], $ex->messageArgs );
		}
	}

	public function testIOErrorSignal() {
		$interpreter = $this->newInterpreter();
		try {
			proc_terminate( $interpreter->proc, 15 );
			// Some dummy protocol interaction to make it see the interpreter went away
			$interpreter->loadString( 'return ...', 'test' );
			$this->fail( 'Expected exception not thrown' );
		} catch ( ScribuntoException $ex ) {
			$this->assertSame( 'scribunto-luastandalone-signal', $ex->getMessageName() );
			$this->assertSame( [ '[UNKNOWN]', 15 ], $ex->messageArgs );
		}
	}

	public function testGetStatus() {
		$startTime = microtime( true );
		if ( php_uname( 's' ) !== 'Linux' ) {
			$this->markTestSkipped( "getStatus() not supported on platforms other than Linux" );
			return;
		}
		$interpreter = $this->newInterpreter();
		$engine = TestingAccessWrapper::newFromObject( $interpreter->engine );
		$status = $interpreter->getStatus();
		$pid = $status['pid'];
		$this->assertIsInt( $status['pid'] );
		$initialVsize = $this->getVsize( $pid );
		$this->assertGreaterThan( 0, $initialVsize, 'Initial vsize' );

		$chunk = $this->getBusyLoop( $interpreter );

		while ( microtime( true ) - $startTime < 1 ) {
			$interpreter->callFunction( $chunk, 100 );
		}
		$status = $interpreter->getStatus();
		$vsize = $this->getVsize( $pid );
		$time = $status['time'] / $engine->getClockTick();
		$this->assertGreaterThan( 0.1, $time, 'getStatus() time usage' );
		$this->assertLessThan( 1.5, $time, 'getStatus() time usage' );
		$this->assertEqualsWithDelta( $vsize, $status['vsize'], $vsize * 0.1, 'vsize' );
	}

	/**
	 * @dataProvider providePhpToLuaArrayKeyConversion
	 */
	public function testPhpToLuaArrayKeyConversion( $array, $expect ) {
		$interpreter = $this->newInterpreter();

		$ret = $interpreter->callFunction(
			$interpreter->loadString(
				'local t, r = ..., {}; for k, v in pairs( t ) do r[v] = type(k) end return r', 'test'
			),
			$array
		);
		ksort( $ret[0], SORT_STRING );
		$this->assertSame( $expect, $ret[0] );
	}

	public static function providePhpToLuaArrayKeyConversion() {
		if ( PHP_INT_MAX > 9007199254740992 ) {
			$a = [
				'9007199254740992' => 'max', '9007199254740993' => 'max+1',
				'-9007199254740992' => 'min', '-9007199254740993' => 'min-1',
			];
		} else {
			$a = [
				'2147483647' => 'max', '2147483648' => 'max+1',
				'-2147483648' => 'min', '-2147483649' => 'min-1',
			];
		}

		return [
			'simple integers' => [
				[ -10 => 'minus ten', 0 => 'zero', 10 => 'ten' ],
				[ 'minus ten' => 'number', 'ten' => 'number', 'zero' => 'number' ],
			],
			'maximal values' => [
				$a,
				[ 'max' => 'number', 'max+1' => 'string', 'min' => 'number', 'min-1' => 'string' ],
			],
		];
	}

	/**
	 * @dataProvider provideLuaToPhpArrayKeyConversion
	 */
	public function testLuaToPhpArrayKeyConversion( $lua, $expect ) {
		if ( $expect instanceof Exception ) {
			$this->expectException( Scribunto_LuaError::class );
			$this->expectExceptionMessage( $expect->getMessage() );
		}

		$interpreter = $this->newInterpreter();
		$ret = $interpreter->callFunction(
			$interpreter->loadString( "return { $lua }", 'test' )
		);
		if ( $expect instanceof Exception ) {
			$this->fail( 'Expected exception not thrown' );
		}
		ksort( $ret[0], SORT_STRING );
		$this->assertSame( $expect, $ret[0] );
	}

	public static function provideLuaToPhpArrayKeyConversion() {
		if ( PHP_INT_MAX > 9007199254740992 ) {
			$max = '9223372036854774784';
			$max2 = '9223372036854775808';
			$min = '-9223372036854775808';
			$min2 = '-9223372036854775809';
		} else {
			$max = '2147483647';
			$max2 = '2147483648';
			$min = '-2147483648';
			$min2 = '-2147483649';
		}

		return [
			'simple integers' => [
				'[-10] = "minus ten", [0] = "zero", [10] = "ten"',
				[ -10 => 'minus ten', 0 => 'zero', 10 => 'ten' ],
			],
			'stringified integers' => [
				'["-10"] = "minus ten", ["0"] = "zero", ["10"] = "ten"',
				[ -10 => 'minus ten', 0 => 'zero', 10 => 'ten' ],
			],
			'maximal integers' => [
				"['$max'] = 'near max', ['$max2'] = 'max+1', ['$min'] = 'min', ['$min2'] = 'min-1'",
				[ $min => 'min', $min2 => 'min-1', $max => 'near max', $max2 => 'max+1' ],
			],
			'collision (0)' => [
				'[0] = "number zero", ["0"] = "string zero"',
				new Exception( 'Collision for array key 0 when passing data from Lua to PHP.' ),
			],
			'collision (float)' => [
				'[1.5] = "number 1.5", ["1.5"] = "string 1.5"',
				new Exception( 'Collision for array key 1.5 when passing data from Lua to PHP.' ),
			],
			'collision (inf)' => [
				'[1/0] = "number inf", ["inf"] = "string inf"',
				new Exception( 'Collision for array key inf when passing data from Lua to PHP.' ),
			],
		];
	}

	public function testFreeFunctions() {
		$interpreter = $this->newInterpreter();

		// Test #1: Make sure freeing actually works
		$ret = $interpreter->callFunction(
			$interpreter->loadString( 'return function() return "testFreeFunction #1" end', 'test' )
		);
		$id = $ret[0]->id;
		$interpreter->cleanupLuaChunks();
		$this->assertEquals(
			[ 'testFreeFunction #1' ], $interpreter->callFunction( $ret[0] ),
			'Test that function #1 was not freed while a reference exists'
		);
		$ret = null;
		$interpreter->cleanupLuaChunks();
		$testfunc = new Scribunto_LuaStandaloneInterpreterFunction( $interpreter->id, $id );
		try {
			$interpreter->callFunction( $testfunc );
			$this->fail( "Expected exception because function #1 should have been freed" );
		} catch ( Scribunto_LuaError $e ) {
			$this->assertEquals(
				"function id $id does not exist", $e->messageArgs[1],
				'Testing for expected error when calling a freed function #1'
			);
		}

		// Test #2: Make sure constructing a new copy of the function works
		$ret = $interpreter->callFunction(
			$interpreter->loadString( 'return function() return "testFreeFunction #2" end', 'test' )
		);
		$id = $ret[0]->id;
		$func = new Scribunto_LuaStandaloneInterpreterFunction( $interpreter->id, $id );
		$ret = null;
		$interpreter->cleanupLuaChunks();
		$this->assertEquals(
			[ 'testFreeFunction #2' ], $interpreter->callFunction( $func ),
			'Test that function #2 was not freed while a reference exists'
		);
		$func = null;
		$interpreter->cleanupLuaChunks();
		$testfunc = new Scribunto_LuaStandaloneInterpreterFunction( $interpreter->id, $id );
		try {
			$interpreter->callFunction( $testfunc );
			$this->fail( "Expected exception because function #2 should have been freed" );
		} catch ( Scribunto_LuaError $e ) {
			$this->assertEquals(
				"function id $id does not exist", $e->messageArgs[1],
				'Testing for expected error when calling a freed function #2'
			);
		}

		// Test #3: Make sure cloning works
		$ret = $interpreter->callFunction(
			$interpreter->loadString( 'return function() return "testFreeFunction #3" end', 'test' )
		);
		$id = $ret[0]->id;
		$func = clone $ret[0];
		$ret = null;
		$interpreter->cleanupLuaChunks();
		$this->assertEquals(
			[ 'testFreeFunction #3' ], $interpreter->callFunction( $func ),
			'Test that function #3 was not freed while a reference exists'
		);
		$func = null;
		$interpreter->cleanupLuaChunks();
		$testfunc = new Scribunto_LuaStandaloneInterpreterFunction( $interpreter->id, $id );
		try {
			$interpreter->callFunction( $testfunc );
			$this->fail( "Expected exception because function #3 should have been freed" );
		} catch ( Scribunto_LuaError $e ) {
			$this->assertEquals(
				"function id $id does not exist", $e->messageArgs[1],
				'Testing for expected error when calling a freed function #3'
			);
		}
	}
}
