<script lang="ts">
	import Chat from '$lib/components/chat/Chat.svelte';
	import { page } from '$app/stores';
	import RightSidebar from '$lib/components/layout/RightSidebar.svelte';

	let chat = null;
</script>

<Chat chatIdProp={$page.params.id} bind:chat />
<RightSidebar bind:chat />