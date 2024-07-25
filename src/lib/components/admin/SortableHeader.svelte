<script lang="ts">
	import ChevronDown from '$lib/components/icons/ChevronDown.svelte';
	import ChevronUp from '../icons/ChevronUp.svelte';

    export let displayName: string;
    export let attributeName: string;
    let ascending = true;

    export let currentAttribute: string;
    export let currentAscending: boolean;

    $: active = attributeName === currentAttribute;

    const clickHandler = () => {
        ascending = !ascending;
        currentAttribute = attributeName;
        currentAscending = ascending;
    }
</script>

<button type="button" class="flex uppercase" on:click={clickHandler}>
    {displayName}
    {#if ascending}
        <ChevronUp className="self-center ml-2 size-3" strokeWidth={active ? "4" : "2"} />
    {:else}
        <ChevronDown className="self-center ml-2 size-3" strokeWidth={active ? "4" : "2"} />
    {/if}
</button>