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

    function fetch_image(prompt){
        return fetch("http://127.0.0.1:5000/?prompt="+encodeURIComponent(prompt)).then((res) => {
            return res.blob();
        });
    }
</script>

<script>
    import {onMount} from "svelte";
    const set_size = 4;
    const attribute_decay = .8;
    const pet = {
        seed: Math.random(),
        base: "a work safe religious creature from another planet",
        age: 1,
        attributes: [],
    }
    let modifiers = [];
    let blob;

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
        let prompt_str = [pet.base, pet.age+" years old"];
        pet.age += 5;
        let weight = 1;
        for (let i=pet.attributes.length-1; i>=0; i--){
            prompt_str.push(pet.attributes[i]+":"+weight.toFixed(4));
            weight *= attribute_decay;
        }
        prompt_str = prompt_str.join(", ");
        // render image on screen
        const blob_raw = await fetch_image(prompt_str);
        const reader = new FileReader();
        reader.onload = (e) => {
            blob = `url(${e.target.result})`;
        };
        reader.readAsDataURL(blob_raw);
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
            box-shadow:0 -.5rem 1rem .5rem rgba(0,0,0,.8);
            max-width:512px;
            max-height:512px;
            width:80%;
            flex-grow:1;
            flex-basis:80%;
            position:relative;
            background-size:cover;
            background-repeat:no-repeat;

            // glass effect
            &::before{
                content:"";
                position:absolute;
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
                left:-10%;
                right:-10%;
                height:10%;
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
    <div class="window" style:background-image={blob}>
        <div class="bwood">
            {#each modifiers as m, mi (m.name)}
                <span on:click={() => select_modifier(m)}>{m.name}</span>
            {/each}
        </div>
    </div>
</main>