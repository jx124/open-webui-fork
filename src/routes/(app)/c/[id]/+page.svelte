<script lang="ts">
	import Chat from '$lib/components/chat/Chat.svelte';
	import { page } from '$app/stores';
	import { onMount } from 'svelte';
	import { updateChatSessionTimes } from '$lib/apis/chats';

	let start = 0;
	let currentPage: string = $page.params.id;
	let visible = true;
	let pageTimeMap: { [key: string]: number } = {};

	$: if (visible) {
		start = Date.now();
	}

	$: if (!visible) {
		updateTimings();
	}

	$: if (visible && currentPage !== $page.params.id) {
		updateTimings();

		currentPage = $page.params.id;
		start = Date.now();
	}

	const updateTimings = () => {
		if (pageTimeMap[currentPage]) {
			pageTimeMap[currentPage] += Math.round((Date.now() - start) / 1000);
		} else {
			pageTimeMap[currentPage] = Math.round((Date.now() - start) / 1000);
		}
	}

	const visibilityHandler = async (event) => {
		if (event.target.visibilityState === "hidden") {
			visible = false;
			sendRequest();
		} else {
			visible = true;
		}
	};

	// keepalive: true allows request to be sent when window is closed
	const sendRequest = async () => updateChatSessionTimes(localStorage.token, pageTimeMap)
		.then(() => {
			pageTimeMap = {};
		});

	const updateAndSendRequest = async () => {
		updateTimings();
		sendRequest();
	}

	onMount(() => {
		start = Date.now();

		return updateAndSendRequest;
	})
</script>

<svelte:window
	on:blur={() => { visible = false; }}
	on:focus={() => { visible = true; }}
	on:visibilitychange={visibilityHandler}
	on:beforeunload={updateAndSendRequest}
	on:pagehide={updateAndSendRequest} />


<Chat chatIdProp={$page.params.id} />