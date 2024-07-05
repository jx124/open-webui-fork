<script lang="ts">
	import Modal from "../common/Modal.svelte";

    export let show = false;
</script>

<Modal bind:show size="sm">
	<div class="text-gray-700 dark:text-gray-100">
		<div class=" flex justify-between dark:text-gray-300 px-5 pt-4">
			<div class=" text-lg font-medium self-center">Provide Feedback</div>
			<button
				class="self-center"
				on:click={() => {
					show = false;
				}}
			>
				<svg
					xmlns="http://www.w3.org/2000/svg"
					viewBox="0 0 20 20"
					fill="currentColor"
					class="w-5 h-5"
				>
					<path
						d="M6.28 5.22a.75.75 0 00-1.06 1.06L8.94 10l-3.72 3.72a.75.75 0 101.06 1.06L10 11.06l3.72 3.72a.75.75 0 101.06-1.06L11.06 10l3.72-3.72a.75.75 0 00-1.06-1.06L10 8.94 6.28 5.22z"
					/>
				</svg>
			</button>
		</div>
		
		<div class="flex flex-col pb-2 px-5 mb-5">
			<div class="self-center text-sm font-normal mr-auto mt-2">
                Thank you for using our tool. Let us know your thoughts:
				<div class="pl-4 pt-2">
					<ul class="list-disc space-y-1">
						<li>Email: 
							<a class="hover:underline" href="mailto:swatroleplay.nus@gmail.com">swatroleplay.nus@gmail.com</a>
						</li>
						<li>Website: 
							<a class="hover:underline" href="https://swatroleplaynus.wixsite.com/swat">https://swatroleplaynus.wixsite.com/swat</a>
						</li>
					</ul>
				</div>
            </div>
		</div>
	</div>
</Modal>
