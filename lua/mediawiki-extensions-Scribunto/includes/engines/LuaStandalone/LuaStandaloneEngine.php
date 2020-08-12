<?php

use MediaWiki\Logger\LoggerFactory;

class Scribunto_LuaStandaloneEngine extends Scribunto_LuaEngine {
	protected static $clockTick;
	/** @var array|bool */
	public $initialStatus;

	/**
	 * @var Scribunto_LuaStandaloneInterpreter
	 */
	protected $interpreter;

	public function load() {
		parent::load();
		if ( php_uname( 's' ) === 'Linux' ) {
			$this->initialStatus = $this->interpreter->getStatus();
		} else {
			$this->initialStatus = false;
		}
	}

	/** @inheritDoc */
	public function getPerformanceCharacteristics() {
		return [
			'phpCallsRequireSerialization' => true,
		];
	}

	/** @inheritDoc */
	public function reportLimitData( ParserOutput $output ) {
		try {
			$this->load();
		} catch ( Exception $e ) {
			return;
		}
		if ( $this->initialStatus ) {
			$status = $this->interpreter->getStatus();
			$output->setLimitReportData( 'scribunto-limitreport-timeusage',
				[
					sprintf( "%.3f", $status['time'] / $this->getClockTick() ),
					// Strip trailing .0s
					rtrim( rtrim( sprintf( "%.3f", $this->options['cpuLimit'] ), '0' ), '.' )
				]
			);
			$output->setLimitReportData( 'scribunto-limitreport-virtmemusage',
				[
					$status['vsize'],
					$this->options['memoryLimit']
				]
			);
			$output->setLimitReportData( 'scribunto-limitreport-estmemusage',
				$status['vsize'] - $this->initialStatus['vsize']
			);
		}
		$logs = $this->getLogBuffer();
		if ( $logs !== '' ) {
			$output->addModules( 'ext.scribunto.logs' );
			$output->setLimitReportData( 'scribunto-limitreport-logs', $logs );
		}
	}

	/** @inheritDoc */
	public function formatLimitData( $key, &$value, &$report, $isHTML, $localize ) {
		global $wgLang;
		$lang = $localize ? $wgLang : Language::factory( 'en' );
		switch ( $key ) {
			case 'scribunto-limitreport-logs':
				if ( $isHTML ) {
					$report .= $this->formatHtmlLogs( $value, $localize );
				}
				return false;
			case 'scribunto-limitreport-virtmemusage':
				$value = array_map( [ $lang, 'formatSize' ], $value );
				break;
			case 'scribunto-limitreport-estmemusage':
				$value = $lang->formatSize( $value );
				break;
		}
		return true;
	}

	/**
	 * @return mixed
	 */
	protected function getClockTick() {
		if ( self::$clockTick === null ) {
			Wikimedia\suppressWarnings();
			self::$clockTick = intval( shell_exec( 'getconf CLK_TCK' ) );
			Wikimedia\restoreWarnings();
			if ( !self::$clockTick ) {
				self::$clockTick = 100;
			}
		}
		return self::$clockTick;
	}

	/**
	 * @return Scribunto_LuaStandaloneInterpreter
	 */
	protected function newInterpreter() {
		return new Scribunto_LuaStandaloneInterpreter( $this, $this->options + [
			'logger' => LoggerFactory::getInstance( 'Scribunto' )
		] );
	}

	/** @inheritDoc */
	public function getSoftwareInfo( array &$software ) {
		$ver = Scribunto_LuaStandaloneInterpreter::getLuaVersion( $this->options );
		if ( $ver !== null ) {
			if ( substr( $ver, 0, 6 ) === 'LuaJIT' ) {
				$software['[http://luajit.org/ LuaJIT]'] = str_replace( 'LuaJIT ', '', $ver );
			} else {
				$software['[http://www.lua.org/ Lua]'] = str_replace( 'Lua ', '', $ver );
			}
		}
	}
}
