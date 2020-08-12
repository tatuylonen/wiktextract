<?php

class Scribunto_LuaSandboxInterpreter extends Scribunto_LuaInterpreter {
	/**
	 * @var Scribunto_LuaEngine
	 */
	public $engine;

	/**
	 * @var LuaSandbox
	 */
	public $sandbox;

	/**
	 * @var bool
	 */
	public $profilerEnabled;

	const SAMPLES = 0;
	const SECONDS = 1;
	const PERCENT = 2;

	/**
	 * Check that php-luasandbox is available and of a recent-enough version
	 * @throws Scribunto_LuaInterpreterNotFoundError
	 * @throws Scribunto_LuaInterpreterBadVersionError
	 */
	public static function checkLuaSandboxVersion() {
		if ( !extension_loaded( 'luasandbox' ) ) {
			throw new Scribunto_LuaInterpreterNotFoundError(
				'The luasandbox extension is not present, this engine cannot be used.' );
		}

		if ( !is_callable( 'LuaSandbox::getVersionInfo' ) ) {
			throw new Scribunto_LuaInterpreterBadVersionError(
				'The luasandbox extension is too old (version 1.6+ is required), ' .
					'this engine cannot be used.'
			);
		}
	}

	/**
	 * @param Scribunto_LuaEngine $engine
	 * @param array $options
	 */
	public function __construct( $engine, array $options ) {
		self::checkLuaSandboxVersion();

		$this->engine = $engine;
		$this->sandbox = new LuaSandbox;
		$this->sandbox->setMemoryLimit( $options['memoryLimit'] );
		$this->sandbox->setCPULimit( $options['cpuLimit'] );
		if ( !isset( $options['profilerPeriod'] ) ) {
			$options['profilerPeriod'] = 0.02;
		}
		if ( $options['profilerPeriod'] ) {
			$this->profilerEnabled = true;
			$this->sandbox->enableProfiler( $options['profilerPeriod'] );
		}
	}

	/**
	 * Convert a LuaSandboxError to a Scribunto_LuaError
	 * @param LuaSandboxError $e
	 * @return Scribunto_LuaError
	 */
	protected function convertSandboxError( LuaSandboxError $e ) {
		$opts = [];
		if ( isset( $e->luaTrace ) ) {
			$opts['trace'] = $e->luaTrace;
		}
		$message = $e->getMessage();
		if ( preg_match( '/^(.*?):(\d+): (.*)$/', $message, $m ) ) {
			$opts['module'] = $m[1];
			$opts['line'] = $m[2];
			$message = $m[3];
		}
		return $this->engine->newLuaError( $message, $opts );
	}

	/**
	 * @param string $text
	 * @param string $chunkName
	 * @return mixed
	 * @throws Scribunto_LuaError
	 */
	public function loadString( $text, $chunkName ) {
		try {
			return $this->sandbox->loadString( $text, $chunkName );
		} catch ( LuaSandboxError $e ) {
			throw $this->convertSandboxError( $e );
		}
	}

	/** @inheritDoc */
	public function registerLibrary( $name, array $functions ) {
		$realLibrary = [];
		foreach ( $functions as $funcName => $callback ) {
			$realLibrary[$funcName] = [
				new Scribunto_LuaSandboxCallback( $callback ),
				$funcName ];
		}
		$this->sandbox->registerLibrary( $name, $realLibrary );

		# TODO: replace this with
		# $this->sandbox->registerVirtualLibrary(
		# 	$name, [ $this, 'callback' ], $functions );
	}

	/** @inheritDoc */
	public function callFunction( $func, ...$args ) {
		try {
			$ret = $func->call( ...$args );
			if ( $ret === false ) {
				// Per the documentation on LuaSandboxFunction::call, a return value
				// of false means that something went wrong and it's PHP's fault,
				// so throw a "real" exception.
				throw new MWException(
					__METHOD__ . ': LuaSandboxFunction::call returned false' );
			}
			return $ret;
		} catch ( LuaSandboxTimeoutError $e ) {
			throw $this->engine->newException( 'scribunto-common-timeout' );
		} catch ( LuaSandboxError $e ) {
			throw $this->convertSandboxError( $e );
		}
	}

	/** @inheritDoc */
	public function wrapPhpFunction( $callable ) {
		return $this->sandbox->wrapPhpFunction( $callable );
	}

	/** @inheritDoc */
	public function isLuaFunction( $object ) {
		return $object instanceof LuaSandboxFunction;
	}

	/**
	 * @return int
	 */
	public function getPeakMemoryUsage() {
		return $this->sandbox->getPeakMemoryUsage();
	}

	/**
	 * @return float
	 */
	public function getCPUUsage() {
		return $this->sandbox->getCPUUsage();
	}

	/**
	 * @param int $units self::SAMPLES, self::SECONDS, or self::PERCENT
	 * @return array
	 */
	public function getProfilerFunctionReport( $units ) {
		if ( $this->profilerEnabled ) {
			static $unitsMap;
			if ( !$unitsMap ) {
				$unitsMap = [
					self::SAMPLES => LuaSandbox::SAMPLES,
					self::SECONDS => LuaSandbox::SECONDS,
					self::PERCENT => LuaSandbox::PERCENT,
				];
			}
			return $this->sandbox->getProfilerFunctionReport( $unitsMap[$units] );
		} else {
			return [];
		}
	}

	public function pauseUsageTimer() {
		$this->sandbox->pauseUsageTimer();
	}

	public function unpauseUsageTimer() {
		$this->sandbox->unpauseUsageTimer();
	}
}
