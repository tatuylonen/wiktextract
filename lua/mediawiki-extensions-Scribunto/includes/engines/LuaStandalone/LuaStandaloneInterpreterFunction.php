<?php


class Scribunto_LuaStandaloneInterpreterFunction {
	public static $anyChunksDestroyed = [];
	public static $activeChunkIds = [];

	/**
	 * @var int
	 */
	public $interpreterId;

	/**
	 * @var int
	 */
	public $id;

	/**
	 * @param int $interpreterId
	 * @param int $id
	 */
	public function __construct( $interpreterId, $id ) {
		$this->interpreterId = $interpreterId;
		$this->id = $id;
		$this->incrementRefCount();
	}

	public function __clone() {
		$this->incrementRefCount();
	}

	public function __wakeup() {
		$this->incrementRefCount();
	}

	public function __destruct() {
		$this->decrementRefCount();
	}

	private function incrementRefCount() {
		if ( !isset( self::$activeChunkIds[$this->interpreterId] ) ) {
			self::$activeChunkIds[$this->interpreterId] = [ $this->id => 1 ];
		} elseif ( !isset( self::$activeChunkIds[$this->interpreterId][$this->id] ) ) {
			self::$activeChunkIds[$this->interpreterId][$this->id] = 1;
		} else {
			self::$activeChunkIds[$this->interpreterId][$this->id]++;
		}
	}

	private function decrementRefCount() {
		if ( isset( self::$activeChunkIds[$this->interpreterId][$this->id] ) ) {
			if ( --self::$activeChunkIds[$this->interpreterId][$this->id] <= 0 ) {
				unset( self::$activeChunkIds[$this->interpreterId][$this->id] );
				self::$anyChunksDestroyed[$this->interpreterId] = true;
			}
		} else {
			self::$anyChunksDestroyed[$this->interpreterId] = true;
		}
	}
}
