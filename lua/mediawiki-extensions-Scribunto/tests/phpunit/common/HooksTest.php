<?php

class ScribuntoHooksTest extends PHPUnit\Framework\TestCase {
	use MediaWikiCoversValidator;

	public function provideContentHandlerDefaultModelFor() {
		return [
			[ 'Module:Foo', CONTENT_MODEL_SCRIBUNTO, true ],
			[ 'Module:Foo/doc', null, true ],
			[ 'Module:Foo/styles.css', 'sanitized-css', true, 'sanitized-css' ],
			[ 'Main Page', null, true ],
		];
	}

	/**
	 * @covers ScribuntoHooks::contentHandlerDefaultModelFor
	 * @dataProvider provideContentHandlerDefaultModelFor
	 */
	public function testContentHandlerDefaultModelFor( $name, $expected,
		$retVal, $before = null
	) {
		$title = Title::newFromText( $name );
		$model = $before;
		$ret = ScribuntoHooks::contentHandlerDefaultModelFor( $title, $model );
		$this->assertSame( $retVal, $ret );
		$this->assertSame( $expected, $model );
	}
}
