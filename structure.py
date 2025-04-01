import requests

url = "https://api.brightdata.com/datasets/v3/trigger"
headers = {
	"Authorization": "Bearer 43f9128d8de0cf8d331ef7a37567b5796ca4b1a307d5672cb02417e3a18e9939",
	"Content-Type": "application/json",
}
params = {
	"dataset_id": "gd_lu702nij2f790tmv9h",
	"include_errors": "true",
	"type": "discover_new",
	"discover_by": "profile_url",
}
data = [
	{"url":"https://www.tiktok.com/@babyariel","num_of_posts":10,"what_to_collect":"Posts & Reposts","start_date":"","end_date":"","post_type":""},
	{"url":"https://www.tiktok.com/@sonyakisa8","num_of_posts":10,"what_to_collect":"Posts & Reposts","start_date":"","end_date":"","post_type":""},
	{"url":"https://www.tiktok.com/@smolfrenz","num_of_posts":10,"what_to_collect":"Posts & Reposts","start_date":"","end_date":"","post_type":""},
]

response = requests.post(url, headers=headers, params=params, json=data)
# print(response.json())