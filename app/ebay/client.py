from browseapi import BrowseAPI


class AutoCorrectBrowseAPI(BrowseAPI):
    _uri = 'https://api.ebay.com/buy/browse/v1'
    _auth_uri = 'https://api.ebay.com/identity/v1/oauth2/token'
    _search_uri = _uri + '/item_summary/search?auto_correct=KEYWORD&'
    _search_by_image_uri = _uri + '/item_summary/search_by_image?'
    _get_item_uri = _uri + '/item/{item_id}?'
    _get_item_by_legacy_id_uri = _uri + '/item/get_item_by_legacy_id?'
    _get_items_by_item_group_uri = _uri + '/item/get_items_by_item_group?'
    _check_compatibility_uri = _uri + '/item/{item_id}/check_compatibility'

    # Client Credential Grant Type

    _credentials_grant_type = 'client_credentials'
    _scope_public_data = 'https://api.ebay.com/oauth/api_scope'
