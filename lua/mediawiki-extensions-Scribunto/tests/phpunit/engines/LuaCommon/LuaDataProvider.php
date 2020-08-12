<?php

class Scribunto_LuaDataProvider implements Iterator {
	protected $engine = null;
	protected $exports = null;
	protected $key = 1;

	/**
	 * @param Scribunto_LuaEngine $engine
	 * @param string $moduleName
	 */
	public function __construct( $engine, $moduleName ) {
		$this->engine = $engine;
		$this->key = 1;
		$module = $engine->fetchModuleFromParser(
			Title::makeTitle( NS_MODULE, $moduleName )
		);
		if ( $module === null ) {
			throw new Exception( "Failed to load module $moduleName" );
		}
		// Calling executeModule with null isn't the best idea, since it brings
		// the whole export table into PHP and throws away metatables and such,
		// but for this use case, we don't have anything like that to worry about
		$this->exports = $engine->executeModule( $module->getInitChunk(), null, null );
	}

	public function destroy() {
		$this->engine = null;
		$this->exports = null;
	}

	public function rewind() {
		$this->key = 1;
	}

	public function valid() {
		return $this->key <= $this->exports['count'];
	}

	public function key() {
		return $this->key;
	}

	public function next() {
		$this->key++;
	}

	public function current() {
		return $this->engine->getInterpreter()->callFunction( $this->exports['provide'], $this->key );
	}

	/**
	 * @param string $key Test to run
	 * @return mixed Test result
	 */
	public function run( $key ) {
		list( $ret ) = $this->engine->getInterpreter()->callFunction( $this->exports['run'], $key );
		return $ret;
	}
}
