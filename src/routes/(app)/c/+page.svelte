<script lang="ts">
	import Chat from '$lib/components/chat/Chat.svelte';
	import RightSidebar from '$lib/components/layout/RightSidebar.svelte';
	import { showRightSidebar } from '$lib/stores';
	import { onMount } from 'svelte';

	let chat = null;

	onMount(() => {
		console.log("/(app)/c page");

		$showRightSidebar = false;
	});
</script>

<Chat bind:chat />
<RightSidebar bind:chat />