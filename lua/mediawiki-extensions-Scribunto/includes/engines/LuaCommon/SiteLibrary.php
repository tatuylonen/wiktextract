<?php

use MediaWiki\MediaWikiServices;

class Scribunto_LuaSiteLibrary extends Scribunto_LuaLibraryBase {
	private static $namespacesCacheLang = null;
	private static $namespacesCache = null;
	private static $interwikiMapCache = [];
	private $pagesInCategoryCache = [];

	public function register() {
		global $wgContLang, $wgNamespaceAliases;

		$lib = [
			'getNsIndex' => [ $this, 'getNsIndex' ],
			'pagesInCategory' => [ $this, 'pagesInCategory' ],
			'pagesInNamespace' => [ $this, 'pagesInNamespace' ],
			'usersInGroup' => [ $this, 'usersInGroup' ],
			'interwikiMap' => [ $this, 'interwikiMap' ],
		];
		$parser = $this->getParser();
		$info = [
			'siteName' => $GLOBALS['wgSitename'],
			'server' => $GLOBALS['wgServer'],
			'scriptPath' => $GLOBALS['wgScriptPath'],
			'stylePath' => $GLOBALS['wgStylePath'],
			'currentVersion' => SpecialVersion::getVersion(
				'', $parser ? $parser->getTargetLanguage() : $wgContLang
			),
		];

		if ( !self::$namespacesCache || self::$namespacesCacheLang !== $wgContLang->getCode() ) {
			$namespaces = [];
			$namespacesByName = [];
			foreach ( $wgContLang->getFormattedNamespaces() as $ns => $title ) {
				$canonical = MWNamespace::getCanonicalName( $ns );
				$namespaces[$ns] = [
					'id' => $ns,
					'name' => $title,
					'canonicalName' => strtr( $canonical, '_', ' ' ),
					'hasSubpages' => MWNamespace::hasSubpages( $ns ),
					'hasGenderDistinction' => MWNamespace::hasGenderDistinction( $ns ),
					'isCapitalized' => MWNamespace::isCapitalized( $ns ),
					'isContent' => MWNamespace::isContent( $ns ),
					'isIncludable' => !MWNamespace::isNonincludable( $ns ),
					'isMovable' => MWNamespace::isMovable( $ns ),
					'isSubject' => MWNamespace::isSubject( $ns ),
					'isTalk' => MWNamespace::isTalk( $ns ),
					'defaultContentModel' => MWNamespace::getNamespaceContentModel( $ns ),
					'aliases' => [],
				];
				if ( $ns >= NS_MAIN ) {
					$namespaces[$ns]['subject'] = MWNamespace::getSubject( $ns );
					$namespaces[$ns]['talk'] = MWNamespace::getTalk( $ns );
					$namespaces[$ns]['associated'] = MWNamespace::getAssociated( $ns );
				} else {
					$namespaces[$ns]['subject'] = $ns;
				}
				$namespacesByName[strtr( $title, ' ', '_' )] = $ns;
				if ( $canonical ) {
					$namespacesByName[$canonical] = $ns;
				}
			}

			$aliases = array_merge( $wgNamespaceAliases, $wgContLang->getNamespaceAliases() );
			foreach ( $aliases as $title => $ns ) {
				if ( !isset( $namespacesByName[$title] ) && isset( $namespaces[$ns] ) ) {
					$ct = count( $namespaces[$ns]['aliases'] );
					$namespaces[$ns]['aliases'][$ct + 1] = $title;
					$namespacesByName[$title] = $ns;
				}
			}

			$namespaces[NS_MAIN]['displayName'] = wfMessage( 'blanknamespace' )->inContentLanguage()->text();

			self::$namespacesCache = $namespaces;
			self::$namespacesCacheLang = $wgContLang->getCode();
		}
		$info['namespaces'] = self::$namespacesCache;

		$info['stats'] = [
			'pages' => (int)SiteStats::pages(),
			'articles' => (int)SiteStats::articles(),
			'files' => (int)SiteStats::images(),
			'edits' => (int)SiteStats::edits(),
			'users' => (int)SiteStats::users(),
			'activeUsers' => (int)SiteStats::activeUsers(),
			'admins' => (int)SiteStats::numberingroup( 'sysop' ),
		];

		return $this->getEngine()->registerInterface( 'mw.site.lua', $lib, $info );
	}

	/**
	 * Handler for pagesInCategory
	 * @internal
	 * @param string|null $category
	 * @param string|null $which
	 * @return int[]|int[][]
	 */
	public function pagesInCategory( $category = null, $which = null ) {
		$this->checkType( 'pagesInCategory', 1, $category, 'string' );
		$this->checkTypeOptional( 'pagesInCategory', 2, $which, 'string', 'all' );

		$title = Title::makeTitleSafe( NS_CATEGORY, $category );
		if ( !$title ) {
			return [ 0 ];
		}
		$cacheKey = $title->getDBkey();

		if ( !isset( $this->pagesInCategoryCache[$cacheKey] ) ) {
			$this->incrementExpensiveFunctionCount();
			$category = Category::newFromTitle( $title );
			$counts = [
				'all' => (int)$category->getPageCount(),
				'subcats' => (int)$category->getSubcatCount(),
				'files' => (int)$category->getFileCount(),
			];
			$counts['pages'] = $counts['all'] - $counts['subcats'] - $counts['files'];
			$this->pagesInCategoryCache[$cacheKey] = $counts;
		}
		if ( $which === '*' ) {
			return [ $this->pagesInCategoryCache[$cacheKey] ];
		}
		if ( !isset( $this->pagesInCategoryCache[$cacheKey][$which] ) ) {
			$this->checkType(
				'pagesInCategory', 2, $which, "one of '*', 'all', 'pages', 'subcats', or 'files'"
			);
		}
		return [ $this->pagesInCategoryCache[$cacheKey][$which] ];
	}

	/**
	 * Handler for pagesInNamespace
	 * @internal
	 * @param int|string|null $ns
	 * @return int[]
	 */
	public function pagesInNamespace( $ns = null ) {
		$this->checkType( 'pagesInNamespace', 1, $ns, 'number' );
		return [ (int)SiteStats::pagesInNs( intval( $ns ) ) ];
	}

	/**
	 * Handler for usersInGroup
	 * @internal
	 * @param string|null $group
	 * @return int[]
	 */
	public function usersInGroup( $group = null ) {
		$this->checkType( 'usersInGroup', 1, $group, 'string' );
		return [ (int)SiteStats::numberingroup( strtolower( $group ) ) ];
	}

	/**
	 * Handler for getNsIndex
	 * @internal
	 * @param string|null $name
	 * @return int[]|bool[]
	 */
	public function getNsIndex( $name = null ) {
		global $wgContLang;
		$this->checkType( 'getNsIndex', 1, $name, 'string' );
		// PHP call is case-insensitive but chokes on non-standard spaces/underscores.
		$name = trim( preg_replace( '/[\s_]+/', '_', $name ), '_' );
		return [ $wgContLang->getNsIndex( $name ) ];
	}

	/**
	 * Handler for interwikiMap
	 * @internal
	 * @param string|null $filter
	 * @return array[]
	 */
	public function interwikiMap( $filter = null ) {
		global $wgLocalInterwikis, $wgExtraInterlanguageLinkPrefixes;
		$this->checkTypeOptional( 'interwikiMap', 1, $filter, 'string', null );
		$local = null;
		if ( $filter === 'local' ) {
			$local = '1';
		} elseif ( $filter === '!local' ) {
			$local = '0';
		} elseif ( $filter !== null ) {
			throw new Scribunto_LuaError(
				"bad argument #1 to 'interwikiMap' (unknown filter '$filter')"
			);
		}
		$cacheKey = $filter === null ? 'null' : $filter;
		if ( !isset( self::$interwikiMapCache[$cacheKey] ) ) {
			// Not expensive because we can have a max of three cache misses in the
			// entire page parse.
			$interwikiMap = [];
			$lookup = MediaWikiServices::getInstance()->getInterwikiLookup();
			$prefixes = $lookup->getAllPrefixes( $local );
			foreach ( $prefixes as $row ) {
				$prefix = $row['iw_prefix'];
				$val = [
					'prefix' => $prefix,
					'url' => wfExpandUrl( $row['iw_url'], PROTO_RELATIVE ),
					'isProtocolRelative' => substr( $row['iw_url'], 0, 2 ) === '//',
					'isLocal' => isset( $row['iw_local'] ) && $row['iw_local'] == '1',
					'isTranscludable' => isset( $row['iw_trans'] ) && $row['iw_trans'] == '1',
					'isCurrentWiki' => in_array( $prefix, $wgLocalInterwikis ),
					'isExtraLanguageLink' => in_array( $prefix, $wgExtraInterlanguageLinkPrefixes ),
				];
				if ( $val['isExtraLanguageLink'] ) {
					$displayText = wfMessage( "interlanguage-link-$prefix" );
					if ( !$displayText->isDisabled() ) {
						$val['displayText'] = $displayText->text();
					}
					$tooltip = wfMessage( "interlanguage-link-sitename-$prefix" );
					if ( !$tooltip->isDisabled() ) {
						$val['tooltip'] = $tooltip->text();
					}
				}
				$interwikiMap[$prefix] = $val;
			}
			self::$interwikiMapCache[$cacheKey] = $interwikiMap;
		}
		return [ self::$interwikiMapCache[$cacheKey] ];
	}
}
