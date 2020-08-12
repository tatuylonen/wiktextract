<?php
/**
 * Scribunto Content Model
 *
 * @file
 * @ingroup Extensions
 * @ingroup Scribunto
 *
 * @author Brad Jorsch <bjorsch@wikimedia.org>
 */

use MediaWiki\MediaWikiServices;

/**
 * Represents the content of a Scribunto script page
 */
class ScribuntoContent extends TextContent {

	/**
	 * @param string $text
	 */
	public function __construct( $text ) {
		parent::__construct( $text, CONTENT_MODEL_SCRIBUNTO );
	}

	/**
	 * Checks whether the script is valid
	 *
	 * @param Title $title
	 * @return Status
	 */
	public function validate( Title $title ) {
		$engine = Scribunto::newDefaultEngine();
		$engine->setTitle( $title );
		return $engine->validate( $this->getText(), $title->getPrefixedDBkey() );
	}

	/** @inheritDoc */
	public function prepareSave( WikiPage $page, $flags, $parentRevId, User $user ) {
		return $this->validate( $page->getTitle() );
	}

	/**
	 * Parse the Content object and generate a ParserOutput from the result.
	 *
	 * @param Title $title The page title to use as a context for rendering
	 * @param null|int $revId The revision being rendered (optional)
	 * @param ParserOptions $options Any parser options
	 * @param bool $generateHtml Whether to generate HTML (default: true).
	 * @param ParserOutput &$output ParserOutput representing the HTML form of the text.
	 * @return ParserOutput
	 */
	protected function fillParserOutput(
		Title $title, $revId, ParserOptions $options, $generateHtml, ParserOutput &$output
	) {
		$parser = MediaWikiServices::getInstance()->getParser();

		$text = $this->getText();

		// Get documentation, if any
		$output = new ParserOutput();
		$doc = Scribunto::getDocPage( $title );
		if ( $doc ) {
			$msg = wfMessage(
				$doc->exists() ? 'scribunto-doc-page-show' : 'scribunto-doc-page-does-not-exist',
				$doc->getPrefixedText()
			)->inContentLanguage();

			if ( !$msg->isDisabled() ) {
				// We need the ParserOutput for categories and such, so we
				// can't use $msg->parse().
				$docViewLang = $doc->getPageViewLanguage();
				$dir = $docViewLang->getDir();

				// Code is forced to be ltr, but the documentation can be rtl.
				// Correct direction class is needed for correct formatting.
				// The possible classes are
				// mw-content-ltr or mw-content-rtl
				$dirClass = "mw-content-$dir";

				$docWikitext = Html::rawElement(
					'div',
					[
						'lang' => $docViewLang->getHtmlCode(),
						'dir' => $dir,
						'class' => $dirClass,
					],
					// Line breaks are needed so that wikitext would be
					// appropriately isolated for correct parsing. See Bug 60664.
					"\n" . $msg->plain() . "\n"
				);

				if ( $options->getTargetLanguage() === null ) {
					$options->setTargetLanguage( $doc->getPageLanguage() );
				}

				$output = $parser->parse( $docWikitext, $title, $options, true, true, $revId );
			}

			// Mark the doc page as a transclusion, so we get purged when it
			// changes.
			$output->addTemplate( $doc, $doc->getArticleID(), $doc->getLatestRevID() );
		}

		// Validate the script, and include an error message and tracking
		// category if it's invalid
		$status = $this->validate( $title );
		if ( !$status->isOK() ) {
			$output->setText( $output->getRawText() .
				Html::rawElement( 'div', [ 'class' => 'errorbox' ],
					$status->getHTML( 'scribunto-error-short', 'scribunto-error-long' )
				)
			);
			$output->addTrackingCategory( 'scribunto-module-with-errors-category', $title );
		}

		if ( !$generateHtml ) {
			// We don't need the actual HTML
			$output->setText( '' );
			return $output;
		}

		$engine = Scribunto::newDefaultEngine();
		$engine->setTitle( $title );
		if ( $this->highlight( $text, $output, $engine ) ) {
			return $output;
		}

		// No GeSHi, or GeSHi can't parse it, use plain <pre>
		$output->setText( $output->getRawText() .
			"<pre class='mw-code mw-script' dir='ltr'>\n" .
			htmlspecialchars( $text ) .
			"\n</pre>\n"
		);

		return $output;
	}

	/**
	 * Adds syntax highlighting to the output (or do not touch it and return false).
	 * @param string $text
	 * @param ParserOutput $output
	 * @param ScribuntoEngineBase $engine
	 * @return bool Success status
	 */
	protected function highlight( $text, ParserOutput $output, ScribuntoEngineBase $engine ) {
		global $wgScribuntoUseGeSHi;
		$language = $engine->getGeSHiLanguage();
		if ( $wgScribuntoUseGeSHi && class_exists( SyntaxHighlight::class ) && $language ) {
			$status = SyntaxHighlight::highlight( $text, $language );
			if ( $status->isGood() ) {
				// @todo replace addModuleStyles line with the appropriate call on
				// SyntaxHighlight once one is created
				$output->addModuleStyles( 'ext.pygments' );
				$output->setText( $output->getRawText() . $status->getValue() );
				return true;
			}
		}
		return false;
	}
}
