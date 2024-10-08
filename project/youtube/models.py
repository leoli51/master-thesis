from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Any, Literal

import dateutil

from project.utils.json import EnhancedJSONEncoder


@dataclass(frozen=True)
class Thumbnail:
	height: int
	url: str
	width: int

	@classmethod
	def from_api_response(cls, api_response) -> Thumbnail:
		return cls(**api_response)


@dataclass(frozen=True)
class SearchResultItem:
	"""
	Check https://developers.google.com/youtube/v3/docs/search for detailed documentation of these fields.
	"""

	channel_id: str
	channel_title: str
	description: str
	id: str
	kind: str
	live_broadcast_content: Literal["upcoming", "live", "none"]
	published_at: datetime
	thumbnails: dict[str, Thumbnail]
	title: str

	@classmethod
	def from_api_response(cls, api_response: Any) -> SearchResultItem:
		return cls(
			channel_id=api_response["snippet"]["channelId"],
			channel_title=api_response["snippet"]["channelTitle"],
			description=api_response["snippet"]["description"],
			id=api_response["id"].get("videoId")
			or api_response["id"].get("channelId")
			or api_response["id"].get("playlistId"),
			kind=api_response["id"]["kind"],
			live_broadcast_content=api_response["snippet"]["liveBroadcastContent"],
			published_at=dateutil.parser.parse(api_response["snippet"]["publishedAt"]),
			thumbnails={
				thumbnail_key: Thumbnail.from_api_response(thumbnail_api_response)
				for thumbnail_key, thumbnail_api_response in api_response["snippet"][
					"thumbnails"
				].items()
			},
			title=api_response["snippet"]["title"],
		)

	@classmethod
	def from_dict(cls, dic: dict[str, Any]) -> SearchResultItem:
		override_dict = {
			"published_at": dateutil.parser.parse(dic["published_at"]),
			"thumbnails": {
				thumbnail_key: Thumbnail(**thumbnail_dict)
				for thumbnail_key, thumbnail_dict in dic["thumbnails"].items()
			},
		}
		return cls(**(dic | override_dict))


if __name__ == "__main__":
	import json

	with open("project/youtube/response_example.json") as response_file:
		response = json.load(response_file)
		models = [SearchResultItem.from_api_response(item_raw) for item_raw in response["items"]]

	with open("project/youtube/serialized_searchresult.json", "w") as serialize_file:
		json.dump(models, serialize_file, cls=EnhancedJSONEncoder)

	with open("project/youtube/serialized_searchresult.json") as serialize_file:
		raw_samples = json.load(serialize_file)
		print(SearchResultItem.from_dict(raw_samples[0]))
