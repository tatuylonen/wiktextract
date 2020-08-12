<?php


class UstringLibraryNormalizationTestProvider extends Scribunto_LuaDataProvider {
	protected $file = null;
	protected $current = null;
	protected static $static = [
		'1E0A 0323;1E0C 0307;0044 0323 0307;1E0C 0307;0044 0323 0307;',
		false
	];

	/**
	 * @param string|null &$message Message to report when skipping
	 * @return bool Whether the test can be run
	 */
	public static function available( &$message = null ) {
		if ( is_readable( __DIR__ . '/NormalizationTest.txt' ) ) {
			return true;
		}
		$message = wordwrap( 'Download the Unicode Normalization Test Suite from ' .
			'http://unicode.org/Public/8.0.0/ucd/NormalizationTest.txt and save as ' .
			__DIR__ . '/NormalizationTest.txt to run normalization tests. Note that ' .
			'running these tests takes quite some time.' );
		return false;
	}

	/**
	 * @param Scribunto_LuaEngine $engine
	 */
	public function __construct( $engine ) {
		parent::__construct( $engine, 'UstringLibraryNormalizationTests' );
		if ( self::available() ) {
			$this->file = fopen( __DIR__ . '/NormalizationTest.txt', 'r' );
		}
		$this->rewind();
	}

	public function destory() {
		if ( $this->file ) {
			fclose( $this->file );
			$this->file = null;
		}
		parent::destory();
	}

	public function rewind() {
		if ( $this->file ) {
			rewind( $this->file );
		}
		$this->key = 0;
		$this->next();
	}

	public function valid() {
		if ( $this->file ) {
			$v = !feof( $this->file );
		} else {
			$v = $this->key < count( self::$static );
		}
		return $v;
	}

	public function current() {
		return $this->current;
	}

	public function next() {
		$this->current = [ null, null, null, null, null, null ];
		while ( $this->valid() ) {
			if ( $this->file ) {
				$line = fgets( $this->file );
			} else {
				$line = self::$static[$this->key];
			}
			$this->key++;
			if ( preg_match( '/^((?:[0-9A-F ]+;){5})/', $line, $m ) ) {
				$line = rtrim( $m[1], ';' );
				$ret = [ $line ];
				foreach ( explode( ';', $line ) as $field ) {
					$args = [];
					foreach ( explode( ' ', $field ) as $char ) {
						$args[] = hexdec( $char );
					}
					$s = pack( 'N*', ...$args );
					$s = mb_convert_encoding( $s, 'UTF-8', 'UTF-32BE' );
					$ret[] = $s;
				}
				$this->current = $ret;
				return;
			}
		}
	}

	/**
	 * Run the normalization test
	 * @param string $c1 Column 1 from NormalizationTest.txt
	 * @param string $c2 Column 2 from NormalizationTest.txt
	 * @param string $c3 Column 3 from NormalizationTest.txt
	 * @param string $c4 Column 4 from NormalizationTest.txt
	 * @param string $c5 Column 5 from NormalizationTest.txt
	 * @return array
	 */
	public function runNorm( $c1, $c2, $c3, $c4, $c5 ) {
		return $this->engine->getInterpreter()->callFunction( $this->exports['run'],
			$c1, $c2, $c3, $c4, $c5
		);
	}
}
