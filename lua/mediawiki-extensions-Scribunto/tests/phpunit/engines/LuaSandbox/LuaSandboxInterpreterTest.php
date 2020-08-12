<?php

if ( !wfIsCLI() ) {
	exit;
}

require_once __DIR__ . '/../LuaCommon/LuaInterpreterTest.php';

/**
 * @group Lua
 * @group LuaSandbox
 * @covers Scribunto_LuaSandboxInterpreter
 */
class Scribunto_LuaSandboxInterpreterTest extends Scribunto_LuaInterpreterTest {
	public $stdOpts = [
		'memoryLimit' => 50000000,
		'cpuLimit' => 30,
	];

	protected function newInterpreter( $opts = [] ) {
		$opts = $opts + $this->stdOpts;
		$engine = new Scribunto_LuaSandboxEngine( $this->stdOpts );
		return new Scribunto_LuaSandboxInterpreter( $engine, $opts );
	}

	public function testGetMemoryUsage() {
		$interpreter = $this->newInterpreter();
		$chunk = $interpreter->loadString( 's = string.rep("x", 1000000)', 'mem' );
		$interpreter->callFunction( $chunk );
		$mem = $interpreter->getPeakMemoryUsage();
		$this->assertGreaterThan( 1000000, $mem, 'memory usage' );
		$this->assertLessThan( 10000000, $mem, 'memory usage' );
	}
}
