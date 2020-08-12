<?php

abstract class Scribunto_LuaInterpreterTest extends PHPUnit\Framework\TestCase {
	use MediaWikiCoversValidator;

	/**
	 * @return Scribunto_LuaInterpreter
	 */
	abstract protected function newInterpreter( $opts = [] );

	protected function setUp() : void {
		parent::setUp();
		try {
			$this->newInterpreter();
		} catch ( Scribunto_LuaInterpreterNotFoundError $e ) {
			$this->markTestSkipped( "interpreter not available" );
		}
	}

	protected function getBusyLoop( $interpreter ) {
		$chunk = $interpreter->loadString( '
			local args = {...}
			local x, i
			local s = string.rep("x", 1000000)
			local n = args[1]
			local e = args[2] and os.clock() + args[2] or nil
			for i = 1, n do
				x = x or string.find(s, "y", 1, true)
				if e and os.clock() >= e then break end
			end',
			'busy' );
		return $chunk;
	}

	/** @dataProvider provideRoundtrip */
	public function testRoundtrip( /*...*/ ) {
		$args = func_get_args();
		$args = $this->normalizeOrder( $args );
		$interpreter = $this->newInterpreter();
		$passthru = $interpreter->loadString( 'return ...', 'passthru' );
		$ret = $interpreter->callFunction( $passthru, ...$args );
		$ret = $this->normalizeOrder( $ret );
		$this->assertSame( $args, $ret );
	}

	/** @dataProvider provideRoundtrip */
	public function testDoubleRoundtrip( /* ... */ ) {
		$args = func_get_args();
		$args = $this->normalizeOrder( $args );

		$interpreter = $this->newInterpreter();
		$interpreter->registerLibrary( 'test',
			[ 'passthru' => [ $this, 'passthru' ] ] );
		$doublePassthru = $interpreter->loadString(
			'return test.passthru(...)', 'doublePassthru' );

		$finalArgs = $args;
		array_unshift( $finalArgs, $doublePassthru );
		$ret = $interpreter->callFunction( ...$finalArgs );
		$ret = $this->normalizeOrder( $ret );
		$this->assertSame( $args, $ret );
	}

	/**
	 * This cannot be done in testRoundtrip and testDoubleRoundtrip, because
	 * assertSame( NAN, NAN ) returns false.
	 */
	public function testRoundtripNAN() {
		$interpreter = $this->newInterpreter();

		$passthru = $interpreter->loadString( 'return ...', 'passthru' );
		$ret = $interpreter->callFunction( $passthru, NAN );
		$this->assertTrue( is_nan( $ret[0] ), 'NaN was not passed through' );

		$interpreter->registerLibrary( 'test',
			[ 'passthru' => [ $this, 'passthru' ] ] );
		$doublePassthru = $interpreter->loadString(
			'return test.passthru(...)', 'doublePassthru' );
		$ret = $interpreter->callFunction( $doublePassthru, NAN );
		$this->assertTrue( is_nan( $ret[0] ), 'NaN was not double passed through' );
	}

	private function normalizeOrder( $a ) {
		ksort( $a );
		foreach ( $a as &$value ) {
			if ( is_array( $value ) ) {
				$value = $this->normalizeOrder( $value );
			}
		}
		return $a;
	}

	public function passthru( /* ... */ ) {
		$args = func_get_args();
		return $args;
	}

	public function provideRoundtrip() {
		return [
			[ 1 ],
			[ true ],
			[ false ],
			[ 'hello' ],
			[ implode( '', array_map( 'chr', range( 0, 255 ) ) ) ],
			[ 1, 2, 3 ],
			[ [] ],
			[ [ 0 => 'foo', 1 => 'bar' ] ],
			[ [ 1 => 'foo', 2 => 'bar' ] ],
			[ [ 'x' => 'foo', 'y' => 'bar', 'z' => [] ] ],
			[ INF ],
			[ -INF ],
			[ 'ok', null, 'ok' ],
			[ null, 'ok' ],
			[ 'ok', null ],
			[ null ],
		];
	}

	public function testTimeLimit() {
		if ( php_uname( 's' ) === 'Darwin' ) {
			$this->markTestSkipped( "Darwin is lacking POSIX timer, skipping CPU time limiting test." );
		}

		$interpreter = $this->newInterpreter( [ 'cpuLimit' => 1 ] );
		$chunk = $this->getBusyLoop( $interpreter );
		try {
			$interpreter->callFunction(
				$chunk,
				1e9, // Arbitrary large quantity of work for the loop
				2 // Early termination condition: 1 second CPU limit plus 1 second "fudge factor"
			);
			$this->fail( "Expected ScribuntoException was not thrown" );
		} catch ( ScribuntoException $ex ) {
			$this->assertSame( 'scribunto-common-timeout', $ex->messageName );
		}
	}

	public function testTestMemoryLimit() {
		$interpreter = $this->newInterpreter( [ 'memoryLimit' => 20 * 1e6 ] );
		$chunk = $interpreter->loadString( '
			t = {}
			for i = 1, 10 do
				t[#t + 1] = string.rep("x" .. i, 1000000)
			end
			',
			'memoryLimit' );
		try {
			$interpreter->callFunction( $chunk );
			$this->fail( "Expected ScribuntoException was not thrown" );
		} catch ( ScribuntoException $ex ) {
			$this->assertSame( 'scribunto-lua-error', $ex->messageName );
			$this->assertSame( 'not enough memory', $ex->messageArgs[1] );
		}
	}

	public function testWrapPHPFunction() {
		$interpreter = $this->newInterpreter();
		$func = $interpreter->wrapPhpFunction( function ( $n ) {
			return [ 42, $n ];
		} );
		$res = $interpreter->callFunction( $func, 'From PHP' );
		$this->assertEquals( [ 42, 'From PHP' ], $res );

		$chunk = $interpreter->loadString( '
			f = ...
			return f( "From Lua" )
			',
			'wrappedPhpFunction' );
		$res = $interpreter->callFunction( $chunk, $func );
		$this->assertEquals( [ 42, 'From Lua' ], $res );
	}

	public function testRegisterInterfaceWithSameName() {
		$interpreter = $this->newInterpreter();
		$test1Called = false;
		$test2Called = false;

		// Like a first call to Scribunto_LuaEngine::registerInterface()
		$interpreter->registerLibrary( 'mw_interface', [
			'foo' => function ( $v ) use ( &$test1Called ) {
				$test1Called = $v;
			},
		] );
		$interpreter->callFunction(
			$interpreter->loadString( 'test1 = mw_interface; mw_interface = nil', 'test' )
		);
		// Like a second call to Scribunto_LuaEngine::registerInterface()
		$interpreter->registerLibrary( 'mw_interface', [
			'foo' => function ( $v ) use ( &$test2Called ) {
				$test2Called = $v;
			},
		] );
		$interpreter->callFunction(
			$interpreter->loadString( 'test2 = mw_interface; mw_interface = nil', 'test' )
		);
		// Call both of the interfaces registered above.
		$interpreter->callFunction(
			$interpreter->loadString( 'test1.foo( "first" ); test2.foo( "second" )', 'test' )
		);
		$this->assertSame( 'first', $test1Called, 'test1.foo was called with "first"' );
		$this->assertSame( 'second', $test2Called, 'test2.foo was called with "second"' );
	}

}
