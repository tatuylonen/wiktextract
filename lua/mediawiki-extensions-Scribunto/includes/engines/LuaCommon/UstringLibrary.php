<?php

use UtfNormal\Validator;

class Scribunto_LuaUstringLibrary extends Scribunto_LuaLibraryBase {
	/**
	 * Limit on pattern lengths, in bytes not characters
	 * @var integer
	 */
	private $patternLengthLimit = 10000;

	/**
	 * Limit on string lengths, in bytes not characters
	 * If null, $wgMaxArticleSize * 1024 will be used
	 * @var integer|null
	 */
	private $stringLengthLimit = null;

	/**
	 * PHP until 5.6.9 are buggy when the regex in preg_replace an
	 * preg_match_all matches the empty string.
	 * @var boolean
	 */
	private $phpBug53823 = false;

	/**
	 * A cache of patterns and the regexes they generate.
	 * @var MapCacheLRU
	 */
	private $patternRegexCache = null;

	/** @inheritDoc */
	public function __construct( $engine ) {
		if ( $this->stringLengthLimit === null ) {
			global $wgMaxArticleSize;
			$this->stringLengthLimit = $wgMaxArticleSize * 1024;
		}

		$this->phpBug53823 = preg_replace( '//us', 'x', "\xc3\xa1" ) === "x\xc3x\xa1x";
		$this->patternRegexCache = new MapCacheLRU( 100 );

		parent::__construct( $engine );
	}

	public function register() {
		$perf = $this->getEngine()->getPerformanceCharacteristics();

		if ( $perf['phpCallsRequireSerialization'] ) {
			$lib = [
				// Pattern matching is still much faster in PHP, even with the
				// overhead of serialization
				'find' => [ $this, 'ustringFind' ],
				'match' => [ $this, 'ustringMatch' ],
				'gmatch_init' => [ $this, 'ustringGmatchInit' ],
				'gmatch_callback' => [ $this, 'ustringGmatchCallback' ],
				'gsub' => [ $this, 'ustringGsub' ],
			];
		} else {
			$lib = [
				'isutf8' => [ $this, 'ustringIsUtf8' ],
				'byteoffset' => [ $this, 'ustringByteoffset' ],
				'codepoint' => [ $this, 'ustringCodepoint' ],
				'gcodepoint_init' => [ $this, 'ustringGcodepointInit' ],
				'toNFC' => [ $this, 'ustringToNFC' ],
				'toNFD' => [ $this, 'ustringToNFD' ],
				'toNFKC' => [ $this, 'ustringToNFKC' ],
				'toNFKD' => [ $this, 'ustringToNFKD' ],
				'char' => [ $this, 'ustringChar' ],
				'len' => [ $this, 'ustringLen' ],
				'sub' => [ $this, 'ustringSub' ],
				'upper' => [ $this, 'ustringUpper' ],
				'lower' => [ $this, 'ustringLower' ],
				'find' => [ $this, 'ustringFind' ],
				'match' => [ $this, 'ustringMatch' ],
				'gmatch_init' => [ $this, 'ustringGmatchInit' ],
				'gmatch_callback' => [ $this, 'ustringGmatchCallback' ],
				'gsub' => [ $this, 'ustringGsub' ],
			];
		}
		return $this->getEngine()->registerInterface( 'mw.ustring.lua', $lib, [
			'stringLengthLimit' => $this->stringLengthLimit,
			'patternLengthLimit' => $this->patternLengthLimit,
		] );
	}

	/**
	 * Check a string first parameter
	 * @param string $name Function name, for errors
	 * @param mixed $s Value to check
	 * @param bool $checkEncoding Whether to validate UTF-8 encoding.
	 */
	private function checkString( $name, $s, $checkEncoding = true ) {
		if ( $this->getLuaType( $s ) == 'number' ) {
			$s = (string)$s;
		} else {
			$this->checkType( $name, 1, $s, 'string' );
			if ( $checkEncoding && !mb_check_encoding( $s, 'UTF-8' ) ) {
				throw new Scribunto_LuaError( "bad argument #1 to '$name' (string is not UTF-8)" );
			}
			if ( strlen( $s ) > $this->stringLengthLimit ) {
				throw new Scribunto_LuaError(
					"bad argument #1 to '$name' (string is longer than $this->stringLengthLimit bytes)"
				);
			}
		}
	}

	/**
	 * Handler for isUtf8
	 * @internal
	 * @param string $s
	 * @return bool[]
	 */
	public function ustringIsUtf8( $s ) {
		$this->checkString( 'isutf8', $s, false );
		return [ mb_check_encoding( $s, 'UTF-8' ) ];
	}

	/**
	 * Handler for byteoffset
	 * @internal
	 * @param string $s
	 * @param int $l
	 * @param int $i
	 * @return int[]|null[]
	 */
	public function ustringByteoffset( $s, $l = 1, $i = 1 ) {
		$this->checkString( 'byteoffset', $s );
		$this->checkTypeOptional( 'byteoffset', 2, $l, 'number', 1 );
		$this->checkTypeOptional( 'byteoffset', 3, $i, 'number', 1 );

		$bytelen = strlen( $s );
		if ( $i < 0 ) {
			$i = $bytelen + $i + 1;
		}
		if ( $i < 1 || $i > $bytelen ) {
			return [ null ];
		}
		$i--;
		$j = $i;
		while ( ( ord( $s[$i] ) & 0xc0 ) === 0x80 ) {
			$i--;
		}
		if ( $l > 0 && $j === $i ) {
			$l--;
		}
		$char = mb_strlen( substr( $s, 0, $i ), 'UTF-8' ) + $l;
		if ( $char < 0 || $char >= mb_strlen( $s, 'UTF-8' ) ) {
			return [ null ];
		} else {
			return [ strlen( mb_substr( $s, 0, $char, 'UTF-8' ) ) + 1 ];
		}
	}

	/**
	 * Handler for codepoint
	 * @internal
	 * @param string $s
	 * @param int $i
	 * @param int|null $j
	 * @return int[]
	 */
	public function ustringCodepoint( $s, $i = 1, $j = null ) {
		$this->checkString( 'codepoint', $s );
		$this->checkTypeOptional( 'codepoint', 2, $i, 'number', 1 );
		$this->checkTypeOptional( 'codepoint', 3, $j, 'number', $i );

		$l = mb_strlen( $s, 'UTF-8' );
		if ( $i < 0 ) {
			$i = $l + $i + 1;
		}
		if ( $j < 0 ) {
			$j = $l + $j + 1;
		}
		if ( $j < $i ) {
			return [];
		}
		$i = max( 1, min( $i, $l + 1 ) );
		$j = max( 1, min( $j, $l + 1 ) );
		$s = mb_substr( $s, $i - 1, $j - $i + 1, 'UTF-8' );
		return unpack( 'N*', mb_convert_encoding( $s, 'UTF-32BE', 'UTF-8' ) );
	}

	/**
	 * Handler for gcodepointInit
	 * @internal
	 * @param string $s
	 * @param int $i
	 * @param int|null $j
	 * @return int[][]
	 */
	public function ustringGcodepointInit( $s, $i = 1, $j = null ) {
		return [ $this->ustringCodepoint( $s, $i, $j ) ];
	}

	/**
	 * Handler for toNFC
	 * @internal
	 * @param string $s
	 * @return string[]|null[]
	 */
	public function ustringToNFC( $s ) {
		$this->checkString( 'toNFC', $s, false );
		if ( !mb_check_encoding( $s, 'UTF-8' ) ) {
			return [ null ];
		}
		return [ Validator::toNFC( $s ) ];
	}

	/**
	 * Handler for toNFD
	 * @internal
	 * @param string $s
	 * @return string[]|null[]
	 */
	public function ustringToNFD( $s ) {
		$this->checkString( 'toNFD', $s, false );
		if ( !mb_check_encoding( $s, 'UTF-8' ) ) {
			return [ null ];
		}
		return [ Validator::toNFD( $s ) ];
	}

	/**
	 * Handler for toNFKC
	 * @internal
	 * @param string $s
	 * @return string[]|null[]
	 */
	public function ustringToNFKC( $s ) {
		$this->checkString( 'toNFKC', $s, false );
		if ( !mb_check_encoding( $s, 'UTF-8' ) ) {
			return [ null ];
		}
		return [ Validator::toNFKC( $s ) ];
	}

	/**
	 * Handler for toNFKD
	 * @internal
	 * @param string $s
	 * @return string[]|null[]
	 */
	public function ustringToNFKD( $s ) {
		$this->checkString( 'toNFKD', $s, false );
		if ( !mb_check_encoding( $s, 'UTF-8' ) ) {
			return [ null ];
		}
		return [ Validator::toNFKD( $s ) ];
	}

	/**
	 * Handler for char
	 * @internal
	 * @return string[]
	 */
	public function ustringChar() {
		$args = func_get_args();
		if ( count( $args ) > $this->stringLengthLimit ) {
			throw new Scribunto_LuaError( "too many arguments to 'char'" );
		}
		foreach ( $args as $k => &$v ) {
			if ( !is_numeric( $v ) ) {
				$this->checkType( 'char', $k + 1, $v, 'number' );
			}
			$v = (int)floor( $v );
			if ( $v < 0 || $v > 0x10ffff ) {
				$k++;
				throw new Scribunto_LuaError( "bad argument #$k to 'char' (value out of range)" );
			}
		}
		$s = pack( 'N*', ...$args );
		$s = mb_convert_encoding( $s, 'UTF-8', 'UTF-32BE' );
		if ( strlen( $s ) > $this->stringLengthLimit ) {
			throw new Scribunto_LuaError( "result to long for 'char'" );
		}
		return [ $s ];
	}

	/**
	 * Handler for len
	 * @internal
	 * @param string $s
	 * @return int[]|null[]
	 */
	public function ustringLen( $s ) {
		$this->checkString( 'len', $s, false );
		if ( !mb_check_encoding( $s, 'UTF-8' ) ) {
			return [ null ];
		}
		return [ mb_strlen( $s, 'UTF-8' ) ];
	}

	/**
	 * Handler for sub
	 * @internal
	 * @param string $s
	 * @param int $i
	 * @param int $j
	 * @return string[]
	 */
	public function ustringSub( $s, $i = 1, $j = -1 ) {
		$this->checkString( 'sub', $s );
		$this->checkTypeOptional( 'sub', 2, $i, 'number', 1 );
		$this->checkTypeOptional( 'sub', 3, $j, 'number', -1 );

		$len = mb_strlen( $s, 'UTF-8' );
		if ( $i < 0 ) {
			$i = $len + $i + 1;
		}
		if ( $j < 0 ) {
			$j = $len + $j + 1;
		}
		if ( $j < $i ) {
			return [ '' ];
		}
		$i = max( 1, min( $i, $len + 1 ) );
		$j = max( 1, min( $j, $len + 1 ) );
		$s = mb_substr( $s, $i - 1, $j - $i + 1, 'UTF-8' );
		return [ $s ];
	}

	/**
	 * Handler for upper
	 * @internal
	 * @param string $s
	 * @return string[]
	 */
	public function ustringUpper( $s ) {
		$this->checkString( 'upper', $s );
		return [ mb_strtoupper( $s, 'UTF-8' ) ];
	}

	/**
	 * Handler for lower
	 * @internal
	 * @param string $s
	 * @return string[]
	 */
	public function ustringLower( $s ) {
		$this->checkString( 'lower', $s );
		return [ mb_strtolower( $s, 'UTF-8' ) ];
	}

	/**
	 * Check a pattern as the second argument
	 * @param string $name Lua function name, for errors
	 * @param mixed $pattern Lua pattern
	 */
	private function checkPattern( $name, $pattern ) {
		if ( $this->getLuaType( $pattern ) == 'number' ) {
			$pattern = (string)$pattern;
		}
		$this->checkType( $name, 2, $pattern, 'string' );
		if ( !mb_check_encoding( $pattern, 'UTF-8' ) ) {
			throw new Scribunto_LuaError( "bad argument #2 to '$name' (string is not UTF-8)" );
		}
		if ( strlen( $pattern ) > $this->patternLengthLimit ) {
			throw new Scribunto_LuaError(
				"bad argument #2 to '$name' (pattern is longer than $this->patternLengthLimit bytes)"
			);
		}
	}

	/**
	 * Convert a Lua pattern into a PCRE regex
	 * @param string $pattern Lua pattern to convert
	 * @param string|false $anchor Regex fragment (`^` or `\G`) to use
	 *  when anchoring the start of the regex, or false to disable start-anchoring.
	 * @param string $name Lua function name, for errors
	 * @return array [ string $re, array $capt, bool $anypos ]
	 *  - $re: The regular expression
	 *  - $capt: Definition of capturing groups, see addCapturesFromMatch()
	 *  - $anypos: Whether any positional captures were encountered in the pattern.
	 */
	private function patternToRegex( $pattern, $anchor, $name ) {
		$cacheKey = serialize( [ $pattern, $anchor ] );
		if ( !$this->patternRegexCache->has( $cacheKey ) ) {
			$this->checkPattern( $name, $pattern );
			$pat = preg_split( '//us', $pattern, null, PREG_SPLIT_NO_EMPTY );

			static $charsets = null, $brcharsets = null;
			if ( $charsets === null ) {
				$charsets = [
					// If you change these, also change lualib/ustring/make-tables.php
					// (and run it to regenerate charsets.lua)
					'a' => '\p{L}',
					'c' => '\p{Cc}',
					'd' => '\p{Nd}',
					'l' => '\p{Ll}',
					'p' => '\p{P}',
					's' => '\p{Xps}',
					'u' => '\p{Lu}',
					'w' => '[\p{L}\p{Nd}]',
					'x' => '[0-9A-Fa-f０-９Ａ-Ｆａ-ｆ]',
					'z' => '\0',

					// These *must* be the inverse of the above
					'A' => '\P{L}',
					'C' => '\P{Cc}',
					'D' => '\P{Nd}',
					'L' => '\P{Ll}',
					'P' => '\P{P}',
					'S' => '\P{Xps}',
					'U' => '\P{Lu}',
					'W' => '[^\p{L}\p{Nd}]',
					'X' => '[^0-9A-Fa-f０-９Ａ-Ｆａ-ｆ]',
					'Z' => '[^\0]',
				];
				$brcharsets = [
					'w' => '\p{L}\p{Nd}',
					'x' => '0-9A-Fa-f０-９Ａ-Ｆａ-ｆ',

					// Negated sets that are not expressable as a simple \P{} are
					// unfortunately complicated.

					// Xan is L plus N, so ^Xan plus Nl plus No is anything that's not L or Nd
					'W' => '\P{Xan}\p{Nl}\p{No}',

					// Manually constructed. Fun.
					'X' => '\x00-\x2f\x3a-\x40\x47-\x60\x67-\x{ff0f}'
						. '\x{ff1a}-\x{ff20}\x{ff27}-\x{ff40}\x{ff47}-\x{10ffff}',

					// Ha!
					'Z' => '\x01-\x{10ffff}',
				] + $charsets;
			}

			$re = '/';
			$len = count( $pat );
			$capt = [];
			$anypos = false;
			$captparen = [];
			$opencapt = [];
			$bct = 0;

			for ( $i = 0; $i < $len; $i++ ) {
				$ii = $i + 1;
				$q = false;
				switch ( $pat[$i] ) {
				case '^':
					$q = $i;
					$re .= ( $anchor === false || $q ) ? '\\^' : $anchor;
					break;

				case '$':
					$q = ( $i < $len - 1 );
					$re .= $q ? '\\$' : '$';
					break;

				case '(':
					if ( $i + 1 >= $len ) {
						throw new Scribunto_LuaError( "Unmatched open-paren at pattern character $ii" );
					}
					$n = count( $capt ) + 1;
					$capt[$n] = ( $pat[$i + 1] === ')' );
					if ( $capt[$n] ) {
						$anypos = true;
					}
					$re .= "(?<m$n>";
					$opencapt[] = $n;
					$captparen[$n] = $ii;
					break;

				case ')':
					if ( count( $opencapt ) <= 0 ) {
						throw new Scribunto_LuaError( "Unmatched close-paren at pattern character $ii" );
					}
					array_pop( $opencapt );
					$re .= $pat[$i];
					break;

				case '%':
					$i++;
					if ( $i >= $len ) {
						throw new Scribunto_LuaError( "malformed pattern (ends with '%')" );
					}
					if ( isset( $charsets[$pat[$i]] ) ) {
						$re .= $charsets[$pat[$i]];
						$q = true;
					} elseif ( $pat[$i] === 'b' ) {
						if ( $i + 2 >= $len ) {
							throw new Scribunto_LuaError( "malformed pattern (missing arguments to \'%b\')" );
						}
						$d1 = preg_quote( $pat[++$i], '/' );
						$d2 = preg_quote( $pat[++$i], '/' );
						if ( $d1 === $d2 ) {
							$re .= "{$d1}[^$d1]*$d1";
						} else {
							$bct++;
							$re .= "(?<b$bct>$d1(?:(?>[^$d1$d2]+)|(?P>b$bct))*$d2)";
						}
					} elseif ( $pat[$i] === 'f' ) {
						if ( $i + 1 >= $len || $pat[++$i] !== '[' ) {
							throw new Scribunto_LuaError( "missing '[' after %f in pattern at pattern character $ii" );
						}
						list( $i, $re2 ) = $this->bracketedCharSetToRegex( $pat, $i, $len, $brcharsets );
						// Because %f considers the beginning and end of the string
						// to be \0, determine if $re2 matches that and take it
						// into account with "^" and "$".
						// @phan-suppress-next-line PhanParamSuspiciousOrder
						if ( preg_match( "/$re2/us", "\0" ) ) {
							$re .= "(?<!^)(?<!$re2)(?=$re2|$)";
						} else {
							$re .= "(?<!$re2)(?=$re2)";
						}
					} elseif ( $pat[$i] >= '0' && $pat[$i] <= '9' ) {
						$n = ord( $pat[$i] ) - 0x30;
						if ( $n === 0 || $n > count( $capt ) || in_array( $n, $opencapt ) ) {
							throw new Scribunto_LuaError( "invalid capture index %$n at pattern character $ii" );
						}
						$re .= "\\g{m$n}";
					} else {
						$re .= preg_quote( $pat[$i], '/' );
						$q = true;
					}
					break;

				case '[':
					list( $i, $re2 ) = $this->bracketedCharSetToRegex( $pat, $i, $len, $brcharsets );
					$re .= $re2;
					$q = true;
					break;

				case ']':
					throw new Scribunto_LuaError( "Unmatched close-bracket at pattern character $ii" );

				case '.':
					$re .= $pat[$i];
					$q = true;
					break;

				default:
					$re .= preg_quote( $pat[$i], '/' );
					$q = true;
					break;
				}
				if ( $q && $i + 1 < $len ) {
					switch ( $pat[$i + 1] ) {
					case '*':
					case '+':
					case '?':
						$re .= $pat[++$i];
						break;
					case '-':
						$re .= '*?';
						$i++;
						break;
					}
				}
			}
			if ( count( $opencapt ) ) {
				$ii = $captparen[$opencapt[0]];
				throw new Scribunto_LuaError( "Unclosed capture beginning at pattern character $ii" );
			}
			$re .= '/us';

			$this->patternRegexCache->set( $cacheKey, [ $re, $capt, $anypos ] );
		}
		return $this->patternRegexCache->get( $cacheKey );
	}

	/**
	 * Convert a Lua pattern bracketed character set to a PCRE regex fragment
	 * @param string[] $pat Pattern being processed, split into individual characters.
	 * @param int $i Offset of the start of the bracketed character set in $pat.
	 * @param int $len Length of $pat.
	 * @param array $brcharsets Mapping from Lua pattern percent escapes to
	 *  regex-style character ranges.
	 * @return array [ int $new_i, string $re_fragment ]
	 */
	private function bracketedCharSetToRegex( $pat, $i, $len, $brcharsets ) {
		$ii = $i + 1;
		$re = '[';
		$i++;
		if ( $i < $len && $pat[$i] === '^' ) {
			$re .= '^';
			$i++;
		}
		for ( $j = $i; $i < $len && ( $j == $i || $pat[$i] !== ']' ); $i++ ) {
			if ( $pat[$i] === '%' ) {
				$i++;
				if ( $i >= $len ) {
					break;
				}
				if ( isset( $brcharsets[$pat[$i]] ) ) {
					$re .= $brcharsets[$pat[$i]];
				} else {
					$re .= preg_quote( $pat[$i], '/' );
				}
			} elseif ( $i + 2 < $len &&
				$pat[$i + 1] === '-' && $pat[$i + 2] !== ']' && $pat[$i + 2] !== '%'
			) {
				if ( $pat[$i] <= $pat[$i + 2] ) {
					$re .= preg_quote( $pat[$i], '/' ) . '-' . preg_quote( $pat[$i + 2], '/' );
				}
				$i += 2;
			} else {
				$re .= preg_quote( $pat[$i], '/' );
			}
		}
		if ( $i >= $len ) {
			throw new Scribunto_LuaError(
				"Missing close-bracket for character set beginning at pattern character $ii"
			);
		}
		$re .= ']';

		// Lua just ignores invalid ranges, while pcre throws an error.
		// We filter them out above, but then we need to special-case empty sets
		if ( $re === '[]' ) {
			// Can't directly quantify (*FAIL), so wrap it.
			// "(?!)" would be simpler and could be quantified if not for a bug in PCRE 8.13 to 8.33
			$re = '(?:(*FAIL))';
		} elseif ( $re === '[^]' ) {
			$re = '.'; // 's' modifier is always used, so this works
		}

		return [ $i, $re ];
	}

	/**
	 * Append captured groups to a result array
	 * @param array $arr Result array to append to.
	 * @param string $s String matched against.
	 * @param array $m Matches, from preg_match with PREG_OFFSET_CAPTURE.
	 * @param array $capt Capture groups (in $m) to process, see patternToRegex()
	 * @param bool $m0_if_no_captures Whether to append "$0" if $capt is empty.
	 * @return array
	 */
	private function addCapturesFromMatch( $arr, $s, $m, $capt, $m0_if_no_captures ) {
		if ( count( $capt ) ) {
			foreach ( $capt as $n => $pos ) {
				if ( $pos ) {
					$o = mb_strlen( substr( $s, 0, $m["m$n"][1] ), 'UTF-8' ) + 1;
					$arr[] = $o;
				} else {
					$arr[] = $m["m$n"][0];
				}
			}
		} elseif ( $m0_if_no_captures ) {
			$arr[] = $m[0][0];
		}
		return $arr;
	}

	/**
	 * Handler for find
	 * @internal
	 * @param string $s
	 * @param string $pattern
	 * @param int $init
	 * @param bool $plain
	 * @return array Format is [ null ], or [ int, int ], or [ int, int, (string|int)... ]
	 */
	public function ustringFind( $s, $pattern, $init = 1, $plain = false ) {
		$this->checkString( 'find', $s );
		$this->checkTypeOptional( 'find', 3, $init, 'number', 1 );
		$this->checkTypeOptional( 'find', 4, $plain, 'boolean', false );

		$len = mb_strlen( $s, 'UTF-8' );
		if ( $init < 0 ) {
			$init = $len + $init + 1;
		} elseif ( $init > $len + 1 ) {
			$init = $len + 1;
		}

		if ( $init > 1 ) {
			$offset = strlen( mb_substr( $s, 0, $init - 1, 'UTF-8' ) );
		} else {
			$init = 1;
			$offset = 0;
		}

		if ( $plain ) {
			$this->checkPattern( 'find', $pattern );
			if ( $pattern !== '' ) {
				$ret = mb_strpos( $s, $pattern, $init - 1, 'UTF-8' );
			} else {
				$ret = $init - 1;
			}
			if ( $ret === false ) {
				return [ null ];
			} else {
				return [ $ret + 1, $ret + mb_strlen( $pattern ) ];
			}
		} else {
			list( $re, $capt ) = $this->patternToRegex( $pattern, '\G', 'find' );
			if ( !preg_match( $re, $s, $m, PREG_OFFSET_CAPTURE, $offset ) ) {
				return [ null ];
			}
			$o = mb_strlen( substr( $s, 0, $m[0][1] ), 'UTF-8' );
			$ret = [ $o + 1, $o + mb_strlen( $m[0][0], 'UTF-8' ) ];
			return $this->addCapturesFromMatch( $ret, $s, $m, $capt, false );
		}
	}

	/**
	 * Handler for match
	 * @internal
	 * @param string $s
	 * @param string $pattern
	 * @param int $init
	 * @return array Format is [ null ] or [ (string|int)... ]
	 */
	public function ustringMatch( $s, $pattern, $init = 1 ) {
		$this->checkString( 'match', $s );
		$this->checkTypeOptional( 'match', 3, $init, 'number', 1 );

		$len = mb_strlen( $s, 'UTF-8' );
		if ( $init < 0 ) {
			$init = $len + $init + 1;
		} elseif ( $init > $len + 1 ) {
			$init = $len + 1;
		}
		if ( $init > 1 ) {
			$offset = strlen( mb_substr( $s, 0, $init - 1, 'UTF-8' ) );
		} else {
			$offset = 0;
		}

		list( $re, $capt ) = $this->patternToRegex( $pattern, '\G', 'match' );
		if ( !preg_match( $re, $s, $m, PREG_OFFSET_CAPTURE, $offset ) ) {
			return [ null ];
		}
		return $this->addCapturesFromMatch( [], $s, $m, $capt, true );
	}

	/**
	 * Handler for gmatchInit
	 * @internal
	 * @param string $s
	 * @param string $pattern
	 * @return array Format is [ string, bool[] ]
	 */
	public function ustringGmatchInit( $s, $pattern ) {
		$this->checkString( 'gmatch', $s );

		list( $re, $capt ) = $this->patternToRegex( $pattern, false, 'gmatch' );
		return [ $re, $capt ];
	}

	/**
	 * Handler for gmatchCallback
	 * @internal
	 * @param string $s
	 * @param string $re
	 * @param bool[] $capt
	 * @param int $pos
	 * @return array Format is [ int, [ null, (string|int)... ] ]
	 */
	public function ustringGmatchCallback( $s, $re, $capt, $pos ) {
		if ( !preg_match( $re, $s, $m, PREG_OFFSET_CAPTURE, $pos ) ) {
			return [ $pos, [] ];
		}
		$pos = $m[0][1] + strlen( $m[0][0] );
		return [ $pos, $this->addCapturesFromMatch( [ null ], $s, $m, $capt, true ) ];
	}

	/**
	 * Handler for gsub
	 * @internal
	 * @param string $s
	 * @param string $pattern
	 * @param mixed $repl
	 * @param string|int|null $n
	 * @return array Format is [ string, int ]
	 */
	public function ustringGsub( $s, $pattern, $repl, $n = null ) {
		$this->checkString( 'gsub', $s );
		$this->checkTypeOptional( 'gsub', 4, $n, 'number', null );

		if ( $n === null ) {
			$n = -1;
		} elseif ( $n < 1 ) {
			return [ $s, 0 ];
		}

		list( $re, $capt, $anypos ) = $this->patternToRegex( $pattern, '^', 'gsub' );
		$captures = [];

		if ( $this->phpBug53823 ) {
			// PHP bug 53823 means that a zero-length match before a UTF-8
			// character will match again before every byte of that character.
			// The workaround is to capture the first "character" of/after the
			// match and verify that its first byte is legal to start a UTF-8
			// character.
			$re = '/(?=(?<phpBug53823>.|$))' . substr( $re, 1 );
		}

		if ( $anypos ) {
			// preg_replace_callback doesn't take a "flags" argument, so we
			// can't pass PREG_OFFSET_CAPTURE to it, which is needed to handle
			// position captures. So instead we have to do a preg_match_all and
			// handle the captures ourself.
			$ct = preg_match_all( $re, $s, $mm, PREG_OFFSET_CAPTURE | PREG_SET_ORDER );
			for ( $i = 0; $i < $ct; $i++ ) {
				$m = $mm[$i];
				if ( $this->phpBug53823 ) {
					$c = ord( $m['phpBug53823'][0] );
					if ( $c >= 0x80 && $c <= 0xbf ) {
						continue;
					}
				}
				$c = [ $m[0][0] ];
				foreach ( $this->addCapturesFromMatch( [], $s, $m, $capt, false ) as $k => $v ) {
					$k++;
					$c["m$k"] = $v;
				}
				$captures[] = $c;
				if ( $n >= 0 && count( $captures ) >= $n ) {
					break;
				}
			}
		}

		switch ( $this->getLuaType( $repl ) ) {
		case 'string':
		case 'number':
			$cb = function ( $m ) use ( $repl, $anypos, &$captures ) {
				if ( $anypos ) {
					$m = array_shift( $captures );
				}
				return preg_replace_callback( '/%([%0-9])/', function ( $m2 ) use ( $m ) {
					$x = $m2[1];
					if ( $x === '%' ) {
						return '%';
					} elseif ( $x === '0' ) {
						return $m[0];
					} elseif ( isset( $m["m$x"] ) ) {
						return $m["m$x"];
					} elseif ( $x === '1' ) {
						// Match undocumented Lua string.gsub behavior
						return $m[0];
					} else {
						throw new Scribunto_LuaError( "invalid capture index %$x in replacement string" );
					}
				}, $repl );
			};
			break;

		case 'table':
			$cb = function ( $m ) use ( $repl, $anypos, &$captures ) {
				if ( $anypos ) {
					$m = array_shift( $captures );
				}
				$x = $m['m1'] ?? $m[0];
				if ( !isset( $repl[$x] ) || $repl[$x] === null ) {
					return $m[0];
				}
				$type = $this->getLuaType( $repl[$x] );
				if ( $type !== 'string' && $type !== 'number' ) {
					throw new Scribunto_LuaError( "invalid replacement value (a $type)" );
				}
				return $repl[$x];
			};
			break;

		case 'function':
			$interpreter = $this->getInterpreter();
			$cb = function ( $m ) use ( $interpreter, $capt, $repl, $anypos, &$captures ) {
				if ( $anypos ) {
					$m = array_shift( $captures );
				}
				$args = [];
				if ( count( $capt ) ) {
					foreach ( $capt as $i => $pos ) {
						$args[] = $m["m$i"];
					}
				} else {
					$args[] = $m[0];
				}
				$ret = $interpreter->callFunction( $repl, ...$args );
				if ( count( $ret ) === 0 || $ret[0] === null ) {
					return $m[0];
				}
				$type = $this->getLuaType( $ret[0] );
				if ( $type !== 'string' && $type !== 'number' ) {
					throw new Scribunto_LuaError( "invalid replacement value (a $type)" );
				}
				return $ret[0];
			};
			break;

		default:
			$this->checkType( 'gsub', 3, $repl, 'function or table or string' );
			throw new LogicException( 'checkType above should have failed' );
		}

		$skippedMatches = 0;
		if ( $this->phpBug53823 ) {
			// Since we're having bogus matches, we need to keep track of the
			// necessary adjustment and stop manually once we hit the limit.
			$maxMatches = $n < 0 ? INF : $n;
			$n = -1;
			$realCallback = $cb;
			$cb = function ( $m ) use ( $realCallback, &$skippedMatches, &$maxMatches ) {
				$c = ord( $m['phpBug53823'] );
				if ( $c >= 0x80 && $c <= 0xbf || $maxMatches <= 0 ) {
					$skippedMatches++;
					return $m[0];
				} else {
					$maxMatches--;
					return $realCallback( $m );
				}
			};
		}

		$count = 0;
		$s2 = preg_replace_callback( $re, $cb, $s, $n, $count );
		if ( $s2 === null ) {
			self::handlePCREError( preg_last_error(), $pattern );
		}
		return [ $s2, $count - $skippedMatches ];
	}

	/**
	 * Handle a PCRE error
	 * @param int $error From preg_last_error()
	 * @param string $pattern Pattern being matched
	 * @throws Scribunto_LuaError
	 */
	private function handlePCREError( $error, $pattern ) {
		$PREG_JIT_STACKLIMIT_ERROR = defined( 'PREG_JIT_STACKLIMIT_ERROR' )
			? PREG_JIT_STACKLIMIT_ERROR
			: 'PREG_JIT_STACKLIMIT_ERROR';

		$error = preg_last_error();
		switch ( $error ) {
			case PREG_NO_ERROR:
				// Huh?
				break;
			case PREG_INTERNAL_ERROR:
				throw new Scribunto_LuaError( "PCRE internal error" );
			case PREG_BACKTRACK_LIMIT_ERROR:
				throw new Scribunto_LuaError(
					"PCRE backtrack limit reached while matching pattern '$pattern'"
				);
			case PREG_RECURSION_LIMIT_ERROR:
				throw new Scribunto_LuaError(
					"PCRE recursion limit reached while matching pattern '$pattern'"
				);
			case PREG_BAD_UTF8_ERROR:
				// Should have alreay been caught, but just in case
				throw new Scribunto_LuaError( "PCRE bad UTF-8 error" );
			case PREG_BAD_UTF8_OFFSET_ERROR:
				// Shouldn't happen, but just in case
				throw new Scribunto_LuaError( "PCRE bad UTF-8 offset error" );
			case $PREG_JIT_STACKLIMIT_ERROR:
				throw new Scribunto_LuaError(
					"PCRE JIT stack limit reached while matching pattern '$pattern'"
				);
			default:
				throw new Scribunto_LuaError(
					"PCRE error code $error while matching pattern '$pattern'"
				);
		}
	}
}
