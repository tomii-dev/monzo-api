from __future__ import annotations

from typing import Dict, Optional

from monzo.authentication import Authentication
from monzo.endpoints.monzo import Monzo
from monzo.exceptions import MonzoArgumentError

FEED_ITEM_TYPES = [
    'basic'
]

FEED_ITEM_PARAMS = {
    'basic': {
        'optional': [
            'body',
            'background_color',
            'title_color',
            'body_color',
        ],
        'required': [
            'title',
            'image_url',
        ]
    }
}


class FeedItem(Monzo):
    __slots__ = [
        '_account_id',
        '_auth',
        '_feed_type',
        '_params',
        '_url',
    ]

    def __init__(
        self,
        auth: Authentication,
        account_id: str,
        feed_type: str,
        params: Dict[str, str],
        url: str = None,
    ):
        """
        Standard init.

        Args:
            auth: Monzo authentication object
            account_id: ID for the account to create the feed item for
            feed_type: Type of feed item to create (must be in FEED_ITEM_TYPES)
            params: Parameters for the feed item.
            url: Optional URL for feed item
        """
        self._account_id: str = account_id
        self._auth: Authentication = auth
        self._feed_type: str = feed_type
        self._params: Dict[str, str] = params
        self._url: Optional[str] = url
        super().__init__(auth=auth)

    def _validate_feed_params(self) -> Dict[str, str]:
        """
        Cleans the params dictionary with the valid params for the feed type.

        Raises:
            MonzoArgumentError: On missing required parameters

        Returns:
            Dictionary of parameters only containing valid keys
        """
        if self._feed_type.lower() not in FEED_ITEM_TYPES:
            raise MonzoArgumentError('Feed type appears invalid')

        parameters_clean = {}

        for parameter in FEED_ITEM_PARAMS[self._feed_type.lower()]['required']:
            if parameter not in self._params:
                raise MonzoArgumentError(f'{parameter} is a required parameter for self._feed_type.lower()')
            parameters_clean[parameter] = self._params[parameter]

        for parameter in FEED_ITEM_PARAMS[self._feed_type.lower()]['optional']:
            if parameter in self._params:
                parameters_clean[parameter] = self._params[parameter]

        return parameters_clean

    def _create(self):
        """
        Creates the feed item record.
        """
        parameters = self._validate_feed_params()
        data = {
            'account_id': self._account_id,
            'type': self._feed_type,
        }
        if self._url:
            data['url'] = self._url
        for parameter in parameters.keys():
            data[f'params[{parameter}]'] = parameters[parameter]
        self._auth.make_request(path='/feed', method='POST', data=data)

    @classmethod
    def create(
        cls,
        auth: Authentication,
        account_id: str,
        feed_type: str,
        params: Dict[str, str],
        url: str = None
    ) -> FeedItem:
        """
        Creates a new feed item.

        Args:
            auth: Monzo authentication object
            account_id: ID for the account to create the feed item for
            feed_type: Type of feed item to create (must be in FEED_ITEM_TYPES)
            params: Parameters for the feed item.
            url: Optional URL for feed item
        """
        feed_item = FeedItem(auth=auth, account_id=account_id, feed_type=feed_type, params=params, url=url)
        feed_item._create()
        return feed_item
