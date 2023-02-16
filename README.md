Install [stablediffusion-webui](https://github.com/AUTOMATIC1111/stable-diffusion-webui).

For good results, use the [dreamshaper model checkpoint](https://civitai.com/models/4384/dreamshaper).

Run webui in API mode:
```
> ./webui.sh --api --cors-allow-origins=*
```

Run the client:
```
> cd client
> npm install
> npm run dev
```

It will give you a link to the local address to view.

- Click an emoji to interact with the pet; each interaction alters how the pet grows older (hover to see a tooltip for what it modifies)
- Refresh to get a new pet

![Screenshot](./screenshot.png?raw=true "Virtual pet screenshot")