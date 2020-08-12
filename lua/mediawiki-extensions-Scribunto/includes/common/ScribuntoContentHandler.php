<?php
/**
 * Scribunto Content Handler
 *
 * @file
 * @ingroup Extensions
 * @ingroup Scribunto
 *
 * @author Brad Jorsch <bjorsch@wikimedia.org>
 */

class ScribuntoContentHandler extends CodeContentHandler {

	/**
	 * @param string $modelId
	 * @param string[] $formats
	 */
	public function __construct(
		$modelId = CONTENT_MODEL_SCRIBUNTO, $formats = [ CONTENT_FORMAT_TEXT ]
	) {
		parent::__construct( $modelId, $formats );
	}

	/**
	 * @return string Class name
	 */
	protected function getContentClass() {
		return ScribuntoContent::class;
	}

	/**
	 * @param string $format
	 * @return bool
	 */
	public function isSupportedFormat( $format ) {
		// An error in an earlier version of Scribunto means we might see this.
		if ( $format === 'CONTENT_FORMAT_TEXT' ) {
			$format = CONTENT_FORMAT_TEXT;
		}
		return parent::isSupportedFormat( $format );
	}

	/**
	 * Only allow this content handler to be used in the Module namespace
	 * @param Title $title
	 * @return bool
	 */
	public function canBeUsedOn( Title $title ) {
		if ( $title->getNamespace() !== NS_MODULE ) {
			return false;
		}

		return parent::canBeUsedOn( $title );
	}
}
