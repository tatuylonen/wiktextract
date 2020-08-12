<?php

/**
 * @covers Scribunto_LuaSandboxEngine
 */
class Scribunto_LuaSandboxTest extends Scribunto_LuaEngineUnitTestBase {
	protected static $moduleName = 'SandboxTests';

	public static function suite( $className ) {
		return self::makeSuite( $className, 'LuaSandbox' );
	}

	protected function getTestModules() {
		return parent::getTestModules() + [
			'SandboxTests' => __DIR__ . '/SandboxTests.lua',
		];
	}

	public function testArgumentParsingTime() {
		$engine = $this->getEngine();
		$parser = $engine->getParser();
		$pp = $parser->getPreprocessor();
		$frame = $pp->newFrame();

		$parser->setHook( 'scribuntodelay', function () {
			$endTime = $this->getRuTime() + 0.5;

			// Waste CPU cycles
			do {
				$t = $this->getRuTime();
			} while ( $t < $endTime );

			return "ok";
		} );
		$this->extraModules['Module:TestArgumentParsingTime'] = '
			return {
				f = function ( frame )
					return frame.args[1]
				end,
				f2 = function ( frame )
					return frame:preprocess( "{{#invoke:TestArgumentParsingTime|f|}}" )
				end,
				f3 = function ( frame )
					return frame:preprocess( "{{#invoke:TestArgumentParsingTime|f|<scribuntodelay/>}}" )
				end,
			}
		';

		// Below we assert that the CPU time counted by LuaSandbox is $delta less than
		// the CPU time actually spent.
		// That way we can make sure that the time spent in the parser hook (which
		// must be more than delta) is not taken into account.
		$delta = 0.25;

		$u0 = $engine->getInterpreter()->getCPUUsage();
		$uTimeBefore = $this->getRuTime();
		$frame->expand(
			$pp->preprocessToObj(
				'{{#invoke:TestArgumentParsingTime|f|<scribuntodelay/>}}'
			)
		);
		$threshold = $this->getRuTime() - $uTimeBefore - $delta;
		$this->assertLessThan( $threshold, $engine->getInterpreter()->getCPUUsage() - $u0,
			'Argument access time was not counted'
		);

		$uTimeBefore = $this->getRuTime();
		$u0 = $engine->getInterpreter()->getCPUUsage();
		$frame->expand(
			$pp->preprocessToObj(
				'{{#invoke:TestArgumentParsingTime|f2|<scribuntodelay/>}}'
			)
		);
		$threshold = $this->getRuTime() - $uTimeBefore - $delta;
		$this->assertLessThan( $threshold, $engine->getInterpreter()->getCPUUsage() - $u0,
			'Unused arguments not counted in preprocess'
		);

		$uTimeBefore = $this->getRuTime();
		$u0 = $engine->getInterpreter()->getCPUUsage();
		$frame->expand(
			$pp->preprocessToObj(
				'{{#invoke:TestArgumentParsingTime|f3}}'
			)
		);
		$threshold = $this->getRuTime() - $uTimeBefore - $delta;
		// If the underlying node is extremely slow, this test might produce false positives
		$this->assertGreaterThan( $threshold, $engine->getInterpreter()->getCPUUsage() - $u0,
			'Recursive argument access time was counted'
		);
	}

	private function getRuTime() {
		$ru = getrusage( 0 /* RUSAGE_SELF */ );
		return $ru['ru_utime.tv_sec'] + $ru['ru_utime.tv_usec'] / 1e6 +
			$ru['ru_stime.tv_sec'] + $ru['ru_stime.tv_usec'] / 1e6;
	}

}
