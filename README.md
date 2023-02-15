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

- Refresh to get a new pet
- Hover emoji to see a tooltip for what it will modify