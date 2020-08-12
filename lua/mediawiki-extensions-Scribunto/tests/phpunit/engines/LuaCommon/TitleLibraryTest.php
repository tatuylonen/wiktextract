<?php

use PHPUnit\Framework\TestSuite;

/**
 * @covers Scribunto_LuaTitleLibrary
 * @group Database
 */
class Scribunto_LuaTitleLibraryTest extends Scribunto_LuaEngineTestBase {
	protected static $moduleName = 'TitleLibraryTests';

	public static function suite( $className ) {
		global $wgInterwikiCache;
		if ( $wgInterwikiCache ) {
			$suite = new TestSuite;
			$suite->setName( $className );
			$suite->addTest(
				new Scribunto_LuaEngineTestSkip(
					$className, 'Cannot run TitleLibrary tests when $wgInterwikiCache is set'
				), [ 'Lua' ]
			);
			return $suite;
		}

		return parent::suite( $className );
	}

	protected function setUp() : void {
		global $wgHooks;

		parent::setUp();

		// Hook to inject our interwiki prefix
		$this->hooks = $wgHooks;
		$wgHooks['InterwikiLoadPrefix'][] = function ( $prefix, &$data ) {
			if ( $prefix !== 'interwikiprefix' ) {
				return true;
			}

			$data = [
				'iw_prefix' => 'interwikiprefix',
				'iw_url'    => '//test.wikipedia.org/wiki/$1',
				'iw_api'    => 1,
				'iw_wikiid' => 0,
				'iw_local'  => 0,
				'iw_trans'  => 0,
			];
			return false;
		};

		// Page for getContent test
		$page = WikiPage::factory( Title::newFromText( 'ScribuntoTestPage' ) );
		$page->doEditContent(
			new WikitextContent(
				'{{int:mainpage}}<includeonly>...</includeonly><noinclude>...</noinclude>'
			),
			'Summary'
		);
		$testPageId = $page->getId();

		// Pages for redirectTarget tests
		$page = WikiPage::factory( Title::newFromText( 'ScribuntoTestRedirect' ) );
		$page->doEditContent(
			new WikitextContent( '#REDIRECT [[ScribuntoTestTarget]]' ),
			'Summary'
		);
		$page = WikiPage::factory( Title::newFromText( 'ScribuntoTestNonRedirect' ) );
		$page->doEditContent(
			new WikitextContent( 'Not a redirect.' ),
			'Summary'
		);

		// Set restrictions for protectionLevels and cascadingProtection tests
		// Since mRestrictionsLoaded is true, they don't count as expensive
		$title = Title::newFromText( 'Main Page' );
		$title->mRestrictionsLoaded = true;
		$title->mRestrictions = [ 'edit' => [], 'move' => [] ];
		$title->mCascadeSources = [
			Title::makeTitle( NS_MAIN, "Lockbox" ),
			Title::makeTitle( NS_MAIN, "Lockbox2" ),
		];
		$title->mCascadingRestrictions = [ 'edit' => [ 'sysop' ] ];
		$title = Title::newFromText( 'Module:TestFramework' );
		$title->mRestrictionsLoaded = true;
		$title->mRestrictions = [
			'edit' => [ 'sysop', 'bogus' ],
			'move' => [ 'sysop', 'bogus' ],
		];
		$title->mCascadeSources = [];
		$title->mCascadingRestrictions = [];
		$title = Title::newFromText( 'interwikiprefix:Module:TestFramework' );
		$title->mRestrictionsLoaded = true;
		$title->mRestrictions = [];
		$title->mCascadeSources = [];
		$title->mCascadingRestrictions = [];
		$title = Title::newFromText( 'Talk:Has/A/Subpage' );
		$title->mRestrictionsLoaded = true;
		$title->mRestrictions = [ 'create' => [ 'sysop' ] ];
		$title->mCascadeSources = [];
		$title->mCascadingRestrictions = [];
		$title = Title::newFromText( 'Not/A/Subpage' );
		$title->mRestrictionsLoaded = true;
		$title->mRestrictions = [ 'edit' => [ 'autoconfirmed' ], 'move' => [ 'sysop' ] ];
		$title->mCascadeSources = [];
		$title->mCascadingRestrictions = [];
		$title = Title::newFromText( 'Module talk:Test Framework' );
		$title->mRestrictionsLoaded = true;
		$title->mRestrictions = [ 'edit' => [], 'move' => [ 'sysop' ] ];
		$title->mCascadeSources = [];
		$title->mCascadingRestrictions = [];

		// Note this depends on every iteration of the data provider running with a clean parser
		$this->getEngine()->getParser()->getOptions()->setExpensiveParserFunctionLimit( 10 );

		// Indicate to the tests that it's safe to create the title objects
		$interpreter = $this->getEngine()->getInterpreter();
		$interpreter->callFunction(
			$interpreter->loadString( "mw.title.testPageId = $testPageId", 'fortest' )
		);

		$this->setMwGlobals( [
			'wgServer' => '//wiki.local',
			'wgCanonicalServer' => 'http://wiki.local',
			'wgUsePathInfo' => true,
			'wgActionPaths' => [],
			'wgScript' => '/w/index.php',
			'wgScriptPath' => '/w',
			'wgArticlePath' => '/wiki/$1',
		] );
	}

	protected function tearDown() : void {
		global $wgHooks;
		$wgHooks = $this->hooks;
		parent::tearDown();
	}

	protected function getTestModules() {
		return parent::getTestModules() + [
			'TitleLibraryTests' => __DIR__ . '/TitleLibraryTests.lua',
		];
	}

	public function testAddsLinks() {
		$engine = $this->getEngine();
		$interpreter = $engine->getInterpreter();

		// Loading a title should create a link
		$links = $engine->getParser()->getOutput()->getLinks();
		$this->assertFalse( isset( $links[NS_PROJECT]['Referenced_from_Lua'] ) );

		$interpreter->callFunction( $interpreter->loadString(
			'local _ = mw.title.new( "Project:Referenced from Lua" ).id', 'reference title'
		) );

		$links = $engine->getParser()->getOutput()->getLinks();
		$this->assertArrayHasKey( NS_PROJECT, $links );
		$this->assertArrayHasKey( 'Referenced_from_Lua', $links[NS_PROJECT] );

		// Loading the page content should create a templatelink
		$templates = $engine->getParser()->getOutput()->getTemplates();
		$this->assertFalse( isset( $links[NS_PROJECT]['Loaded_from_Lua'] ) );

		$interpreter->callFunction( $interpreter->loadString(
			'mw.title.new( "Project:Loaded from Lua" ):getContent()', 'load title'
		) );

		$templates = $engine->getParser()->getOutput()->getTemplates();
		$this->assertArrayHasKey( NS_PROJECT, $templates );
		$this->assertArrayHasKey( 'Loaded_from_Lua', $templates[NS_PROJECT] );
	}
}
