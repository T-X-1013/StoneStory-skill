# Character Routing

当前 StoneStory plugin 只支持两个角色：

- `jia-baoyu` -> 贾宝玉
- `lin-daiyu` -> 林黛玉

若用户没有明确给出角色：

1. 先询问角色
2. 不要自行假定为其中一个

若用户在 slash 命令中已经明确指定：

- 直接按该角色构造 `prompt_payload.json`

若用户提供不支持的角色：

- 明确说明当前只支持贾宝玉和林黛玉
