<?php

class Scribunto_LuaEngineTestSkip extends PHPUnit\Framework\TestCase {
	private $className = '';
	private $message = '';

	/**
	 * @param string $className Class being skipped
	 * @param string $message Skip message
	 */
	public function __construct( $className = '', $message = '' ) {
		$this->className = $className;
		$this->message = $message;
		parent::__construct( 'testDummy' );
	}

	public function testDummy() {
		if ( $this->className ) {
			$this->markTestSkipped( $this->message );
		} else {
			// Dummy
			$this->assertTrue( true );
		}
	}

	public function toString(): string {
		return $this->className;
	}
}
