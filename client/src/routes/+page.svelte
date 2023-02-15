<script context="module">
    import fetch from "cross-fetch";
    import seed from "seed-random";

    const rand = seed("virtual pet");
    // https://stackoverflow.com/questions/2450954/how-to-randomize-shuffle-a-javascript-array
    // modified slightly to make seeded
    function shuffle(array) {
        for (var i = array.length - 1; i > 0; i--) {
            var j = Math.floor(rand() * (i + 1));
            var temp = array[i];
            array[i] = array[j];
            array[j] = temp;
        }
    }

    let adjectives = null;
    let emojis = null;
    let data_loaded = false;
    let loaded_listeners = [];
    let num_modifiers;

    function random_modifier(){
        let idx = Math.floor(Math.random()*num_modifiers);
        return {
            name: emojis[idx],
            word: adjectives[idx] 
        }
    }
   
    let requests = 0;
    fetch("/static/emoji.json").then(async (data) => {
        const emoji_info = await data.json();
        emojis = [];
        for (const v of emoji_info){
            // blacklist certain emoji groups
            const c = v.category;
            if (c === "Flags")
                continue;
            emojis.push(v.emoji);
        }
        // console.log(emojis);
        if (++requests == 2)
            finalize_data();
    }).catch((err) => {
        console.error("failed to fetch emoji list:", err);
    });
    fetch("/static/english-adjectives.txt").then(async (data) => {
        adjectives = await data.text();
        adjectives = adjectives.trim().split(/\s+/);
        if (++requests == 2)
            finalize_data();
    }).catch((err) => {
        console.error("failed to fetch adjective list:", err);
    });

    function finalize_data(){
        if (emojis && adjectives){
            shuffle(emojis);
            shuffle(adjectives);
            num_modifiers = Math.min(emojis.length, adjectives.length);
            console.log("modifier count:", num_modifiers);
            data_loaded = true;
            for (const l of loaded_listeners)
                l();
        }
        else{
            data_loaded = "error";
            console.error("promise was rejected");
            // window.alert("Failed to load app, try refreshing");
        }
    }

    function fetch_image(seed, prev_img, prompt){
        const params = {
            sampler_name: "DPM++ SDE Karras",
            // sampler_name: "DPM fast",
            steps: 20,
            override_settings: {
                do_not_add_watermark: true,
                // sd_model_checkpoint: "dreamshaper_332BakedVaeClipFix.safetensors [13dfc9921f]",
            },
            seed: Math.floor(Math.random()*100000000),
            prompt,
            denoising_strength: 0.5,
            negative_prompt: "((watermark)), ((signature)), sphere, orb, ball, canvas frame, cartoon, 3d, ((bad art)), ((close up)),((b&w)), wierd colors, blurry, (((duplicate))), [out of frame], blurry, ugly, Photoshop, video game, ugly, tiling, out of frame, body out of frame, blurry, 3d render"
        };
        let endpoint = "txt2img";
        if (prev_img){
            console.log("using image as base:", prev_img)
            endpoint = "img2img";
            params.init_images = [prev_img];
            params.include_init_images = true;
        }
        return fetch("http://localhost:7860/sdapi/v1/"+endpoint, {
            method: "POST",
            body: JSON.stringify(params),
            headers: {
                "Content-Type": "application/json"
            },
            credentials: "omit"
        }).then(data => data.json()).then(json => {
            return "data:image/png;base64,"+json.images[0];
        });
    }
</script>

<script>
    import {onMount} from "svelte";
    const age_increment = 7;
    const set_size = 4;
    const attribute_decay = .8;
    const pet = {
        seed: Math.round(Math.random()*10000000),
        base: "creature from another planet, hyperrealistic, beautiful 4k photograph, octane render, natural colors, Bokeh, Wildlife Photography, DSLR, Nikon D750, Lens Distortion",
        age: 1,
        attributes: [],
    }
    let modifiers = [];
    let blob = ["",""];
    let active_blob = 0;

    function next_set(){
        for (let i=0; i<set_size; i++)
            modifiers[i] = random_modifier();
        modifiers = modifiers;
    }

    function select_modifier(m){
        pet.attributes.push(m.word);
        generate_text();
    }

    async function generate_text(initial=false){
        if (!initial)
            next_set();
        let prompt_str = [pet.age+ " years old "+pet.base];
        pet.age += age_increment;
        for (let i=pet.attributes.length-1; i>=0; i--){
            const w = .5*((i+1)/pet.attributes.length) + .5;
            prompt_str.push(`(${pet.attributes[i]}:${w.toFixed(4)})`);
        }
        prompt_str = prompt_str.join(", ");
        console.log("fetching image:", prompt_str);
        // render image on screen; double buffered for transition effect
        const b64 = await fetch_image(pet.seed, blob[active_blob], prompt_str);
        active_blob ^= 1;
        blob[active_blob] = b64;
        blob = blob;
    }

    onMount(() => {
        generate_text(true);
        if (!data_loaded)
            loaded_listeners.push(next_set);
        else next_set();
    });
</script>

<style lang="scss" type="text/scss">
    @font-face{
        font-family: "emoji";
        src: url(/static/emoji.ttf);
    }
    :global(body), :global(html){
        margin:0;
        padding:0;
        height:100%;
        width:100%;
        overflow:hidden;
        display:block;
    }
    :global(body){
        background: url(/static/concrete_e.jpg);
    }
    main{
        display:flex;
        flex-direction: column;
        justify-content: center;
        align-items: center;
        min-height:100%;
        width:100%;
        
        .window{
            background-color: black;
            max-width:512px;
            max-height:512px;
            width:80%;
            flex-grow:1;
            flex-basis:80%;
            position:relative;
            background-size:cover;
            background-repeat:no-repeat;
            border:1.5rem solid #373737;
            border-bottom-width:0;
            border-top-color:black;
	        box-shadow:0 0 2rem black inset;

            &>img{
                position:absolute;
                width:100%;
                height:100%;
                left:0;
                top:0;
                opacity:0;
                filter:blur(1rem);
                transition:opacity 1000ms linear, filter 1000ms linear;
                // z-index:1;
                &.active{
                    opacity:1;
                    filter:blur(0rem);
                    // z-index:2;
                }
            }

            // glass effect
            &::before{
                content:"";
                position:absolute;
                z-index:3;
                left:0;
                right:0;
                top:0;
                bottom:0;
                background:
                    radial-gradient(
                        110% 90% at 100% 120%,
                        rgba(255, 255, 255, .1) 0%,
                        rgba(255, 255, 255, .2) 98%,
                        transparent 100%);
            }

            .bwood{
                background:url(/static/wood_h.jpg);
                margin-left:-10%;
                position:absolute;
                bottom:-10%;
                left:0%;
                right:-10%;
                height:10%;
                box-sizing:border-box;
                box-shadow:0 1rem 2rem .5rem rgba(0,0,0,.8);
                border-radius:.5rem;
                border-top:.25rem solid rgb(90, 32, 1);
                display:flex;
                flex-direction:row;
                align-items:center;
                justify-content: center;
                font-size: 2rem;
                font-family: emoji, monospace;
                overflow:hidden;
                &>span{
                    margin:1rem;
                    filter:drop-shadow(0 0 .5rem rgba(0,0,0,.6));
                    cursor:pointer;
                    transition:transform 100ms;
                    &:hover{
                        transform:scale(130%);
                    }
                }
            }
        }
    }

</style>

<main>
    <div class="window">
        <img src={blob[0]} class:active={active_blob == 0}>
        <img src={blob[1]} class:active={active_blob == 1}>
        <div class="bwood">
            {#each modifiers as m, mi (mi)}
                <span on:click={() => select_modifier(m)} title={m.word}>{m.name}</span>
            {/each}
        </div>
    </div>
</main>