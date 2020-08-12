<?php

class Scribunto_LuaSandboxCallback {

	/**
	 * @var callable
	 */
	protected $callback;

	/**
	 * @param callable $callback
	 */
	public function __construct( $callback ) {
		$this->callback = $callback;
	}

	/**
	 * We use __call with a variable function name so that LuaSandbox will be
	 * able to return a meaningful function name in profiling data.
	 * @param string $funcName
	 * @param array $args
	 * @return mixed
	 */
	public function __call( $funcName, $args ) {
		try {
			return ( $this->callback )( ...$args );
		} catch ( Scribunto_LuaError $e ) {
			throw new LuaSandboxRuntimeError( $e->getLuaMessage() );
		}
	}
}
