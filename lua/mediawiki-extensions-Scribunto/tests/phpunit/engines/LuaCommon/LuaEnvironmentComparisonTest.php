<?php

/**
 * @group Lua
 * @group LuaSandbox
 * @group LuaStandalone
 * @coversNothing
 */
class Scribunto_LuaEnvironmentComparisonTest extends PHPUnit\Framework\TestCase {
	use MediaWikiCoversValidator;

	public $sandboxOpts = [
		'memoryLimit' => 50000000,
		'cpuLimit' => 30,
		'allowEnvFuncs' => true,
	];
	public $standaloneOpts = [
		'errorFile' => null,
		'luaPath' => null,
		'memoryLimit' => 50000000,
		'cpuLimit' => 30,
		'allowEnvFuncs' => true,
	];

	protected $engines = [];

	private function makeEngine( $class, $opts ) {
		$parser = new Parser;
		$options = new ParserOptions;
		$options->setTemplateCallback( [ $this, 'templateCallback' ] );
		$parser->startExternalParse( Title::newMainPage(), $options, Parser::OT_HTML, true );
		$engine = new $class ( [ 'parser' => $parser ] + $opts );
		$parser->scribunto_engine = $engine;
		$engine->setTitle( $parser->getTitle() );
		$engine->getInterpreter();
		return $engine;
	}

	protected function setUp() : void {
		parent::setUp();

		try {
			$this->engines['LuaSandbox'] = $this->makeEngine(
				Scribunto_LuaSandboxEngine::class, $this->sandboxOpts
			);
		} catch ( Scribunto_LuaInterpreterNotFoundError $e ) {
			$this->markTestSkipped( "LuaSandbox interpreter not available" );
			return;
		}

		try {
			$this->engines['LuaStandalone'] = $this->makeEngine(
				Scribunto_LuaStandaloneEngine::class, $this->standaloneOpts
			);
		} catch ( Scribunto_LuaInterpreterNotFoundError $e ) {
			$this->markTestSkipped( "LuaStandalone interpreter not available" );
			return;
		}
	}

	protected function tearDown() : void {
		foreach ( $this->engines as $engine ) {
			$engine->destroy();
		}
		$this->engines = [];
		parent::tearDown();
	}

	private function getGlobalEnvironment( $engine ) {
		static $script = <<<LUA
			xxxseen = {}
			function xxxGetTable( t )
				if xxxseen[t] then
					return 'table'
				end
				local ret = {}
				xxxseen[t] = ret
				for k, v in pairs( t ) do
					if k ~= '_G' and string.sub( k, 1, 3 ) ~= 'xxx' then
						if type( v ) == 'table' then
							ret[k] = xxxGetTable( v )
						elseif type( v ) == 'string'
							or type( v ) == 'number'
							or type( v ) == 'boolean'
							or type( v ) == 'nil'
						then
							ret[k] = v
						else
							ret[k] = type( v )
						end
					end
				end
				return ret
			end
			return xxxGetTable( _G )
LUA;
		$func = $engine->getInterpreter()->loadString( $script, 'script' );
		return $engine->getInterpreter()->callFunction( $func );
	}

	public function testGlobalEnvironment() {
		// Grab the first engine as the "standard"
		$firstEngine = reset( $this->engines );
		$firstName = key( $this->engines );
		$firstEnv = $this->getGlobalEnvironment( $firstEngine );

		// Test all others against it
		foreach ( $this->engines as $secondName => $secondEngine ) {
			if ( $secondName !== $firstName ) {
				$secondEnv = $this->getGlobalEnvironment( $secondEngine );
				$this->assertEquals( $firstEnv, $secondEnv,
					"Environments for $firstName and $secondName are not equivalent" );
			}
		}
	}
}
