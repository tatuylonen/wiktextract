<?php

/**
 * Wikitext scripting infrastructure for MediaWiki: base classes.
 * Copyright (C) 2012 Victor Vasiliev <vasilvv@gmail.com> et al
 * https://www.mediawiki.org/
 *
 * This program is free software; you can redistribute it and/or modify
 * it under the terms of the GNU General Public License as published by
 * the Free Software Foundation; either version 2 of the License, or
 * (at your option) any later version.
 *
 * This program is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
 * GNU General Public License for more details.
 *
 * You should have received a copy of the GNU General Public License along
 * with this program; if not, write to the Free Software Foundation, Inc.,
 * 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA.
 * http://www.gnu.org/copyleft/gpl.html
 */

/**
 * Class that represents a module. Responsible for initial module parsing
 * and maintaining the contents of the module.
 */
abstract class ScribuntoModuleBase {
	/**
	 * @var ScribuntoEngineBase
	 */
	protected $engine;

	/**
	 * @var string
	 */
	protected $code;

	/**
	 * @var string|bool
	 */
	protected $chunkName;

	/**
	 * @param ScribuntoEngineBase $engine
	 * @param string $code
	 * @param string|bool $chunkName
	 */
	public function __construct( ScribuntoEngineBase $engine, $code, $chunkName ) {
		$this->engine = $engine;
		$this->code = $code;
		$this->chunkName = $chunkName;
	}

	/**
	 * @return ScribuntoEngineBase
	 */
	public function getEngine() {
		return $this->engine;
	}

	/**
	 * @return string
	 */
	public function getCode() {
		return $this->code;
	}

	/**
	 * @return string|bool
	 */
	public function getChunkName() {
		return $this->chunkName;
	}

	/**
	 * Validates the script and returns a Status object containing the syntax
	 * errors for the given code.
	 *
	 * @return Status
	 */
	abstract public function validate();

	/**
	 * Invoke the function with the specified name.
	 *
	 * @param string $name
	 * @param PPFrame $frame
	 * @return string
	 */
	abstract public function invoke( $name, $frame );
}
