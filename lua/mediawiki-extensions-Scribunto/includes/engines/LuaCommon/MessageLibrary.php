<?php

class Scribunto_LuaMessageLibrary extends Scribunto_LuaLibraryBase {
	public function register() {
		$lib = [
			'plain' => [ $this, 'messagePlain' ],
			'check' => [ $this, 'messageCheck' ],
		];

		// Get the correct default language from the parser
		if ( $this->getParser() ) {
			$lang = $this->getParser()->getTargetLanguage();
		} else {
			global $wgContLang;
			$lang = $wgContLang;
		}

		return $this->getEngine()->registerInterface( 'mw.message.lua', $lib, [
			'lang' => $lang->getCode(),
		] );
	}

	/**
	 * Create a Message
	 * @param array $data
	 *  - 'rawMessage': (string, optional) If set, create a RawMessage using this as `$text`
	 *  - 'keys': (string|string[]) Message keys. Required unless 'rawMessage' is set.
	 *  - 'lang': (Language|StubUserLang|string) Language for the Message.
	 *  - 'useDB': (bool) "Use database" flag.
	 *  - 'params': (array) Parameters for the Message. May be omitted if $setParams is false.
	 * @param bool $setParams Whether to use $data['params']
	 * @return Message
	 */
	private function makeMessage( $data, $setParams ) {
		if ( isset( $data['rawMessage'] ) ) {
			$msg = new RawMessage( $data['rawMessage'] );
		} else {
			$msg = Message::newFallbackSequence( $data['keys'] );
		}
		$msg->inLanguage( $data['lang'] )
			->useDatabase( $data['useDB'] );
		if ( $setParams ) {
			$msg->params( array_values( $data['params'] ) );
		}
		return $msg;
	}

	/**
	 * Handler for messagePlain
	 * @internal
	 * @param array $data
	 * @return string[]
	 */
	public function messagePlain( $data ) {
		try {
			$msg = $this->makeMessage( $data, true );
			return [ $msg->plain() ];
		} catch ( MWException $ex ) {
			throw new Scribunto_LuaError( "msg:plain() failed (" . $ex->getMessage() . ")" );
		}
	}

	/**
	 * Handler for messageCheck
	 * @internal
	 * @param string $what
	 * @param array $data
	 * @return bool[]
	 */
	public function messageCheck( $what, $data ) {
		if ( !in_array( $what, [ 'exists', 'isBlank', 'isDisabled' ] ) ) {
			throw new Scribunto_LuaError( "invalid what for 'messageCheck'" );
		}

		try {
			$msg = $this->makeMessage( $data, false );
			return [ call_user_func( [ $msg, $what ] ) ];
		} catch ( MWException $ex ) {
			throw new Scribunto_LuaError( "msg:$what() failed (" . $ex->getMessage() . ")" );
		}
	}
}
