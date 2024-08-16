<script lang="ts">
	import { toast } from 'svelte-sonner';

	import { goto } from '$app/navigation';
	import { classes, prompts } from '$lib/stores';
	import { onMount, tick, getContext } from 'svelte';

	import { createNewPrompt, getPrompts, type PromptForm } from '$lib/apis/prompts';
	import PreviewModal from '$lib/components/workspace/PreviewModal.svelte';
	import { canvasPixelTest, generateInitialsImage } from '$lib/utils';
	import { getClassList } from '$lib/apis/classes';
	import ClassMultiSelector from '$lib/components/workspace/ClassMultiSelector.svelte';

	const i18n = getContext('i18n');

	let loading = false;

	let form_data: PromptForm = {
		command: "",
		title: "",
		content: "",
		is_visible: false,
		additional_info: "",

		image_url: "/user.png",
		deadline: null,
		evaluation_id: null,
		selected_model_id: null,

		assigned_classes: []
	};

	let showPreviewModal = false;

	$: form_data.command = form_data.title !== '' ? `${form_data.title.replace(/\s+/g, '-').toLowerCase()}` : '';

	let profileImageInputElement: HTMLInputElement;
	let hasDeadline = false;
	let selectedDateTime: string | null;

	let classItems: {
		label: string,
		value: number
	}[];

	const submitHandler = async () => {
		loading = true;

		if (validateCommandString(form_data.command)) {
			const prompt = await createNewPrompt(
				localStorage.token, form_data
			).catch(
				(error) => {
					toast.error(error);

					return null;
				}
			);

			if (prompt) {
				await prompts.set(await getPrompts(localStorage.token));
				await goto('/workspace/prompts');
			}
		} else {
			toast.error(
				$i18n.t('Only alphanumeric characters and hyphens are allowed in the command string.')
			);
		}

		loading = false;
	};

	const validateCommandString = (inputString: string) => {
		// Regular expression to match only alphanumeric characters and hyphen
		const regex = /^[a-zA-Z0-9-]+$/;

		// Test the input string against the regular expression
		return regex.test(inputString);
	};

	onMount(async () => {
		window.addEventListener('message', async (event) => {
			if (
				!['https://openwebui.com', 'https://www.openwebui.com', 'http://localhost:5173'].includes(
					event.origin
				)
			)
				return;
			const prompt = JSON.parse(event.data);
			console.log(prompt);

			form_data.title = prompt.title;
			await tick();
			form_data.content = prompt.content;
			form_data.command = prompt.command;
			form_data.is_visible = prompt.is_visible;
		});

		if (window.opener ?? false) {
			window.opener.postMessage('loaded', '*');
		}

		if (sessionStorage.prompt) {
			const prompt = JSON.parse(sessionStorage.prompt);

			console.log(prompt);
			form_data.title = prompt.title;
			await tick();
			form_data.content = prompt.content;
			form_data.command = prompt.command.at(0) === '/' ? prompt.command.slice(1) : prompt.command;
			form_data.is_visible = prompt.is_visible;

			sessionStorage.removeItem('prompt');
		}

		$classes = await getClassList(localStorage.token).catch((error) => {
			toast.error(error);
		})

		classItems = $classes.map((c) => {
			return {
				label: c.name,
				value: c.id,
			};
		})
	});
</script>

<PreviewModal bind:show={showPreviewModal} bind:previewContent={form_data.additional_info}/>

<div class="w-full max-h-full">
	<button
		class="flex space-x-1"
		on:click={() => {
			history.back();
		}}
	>
		<div class=" self-center">
			<svg
				xmlns="http://www.w3.org/2000/svg"
				viewBox="0 0 20 20"
				fill="currentColor"
				class="w-4 h-4"
			>
				<path
					fill-rule="evenodd"
					d="M17 10a.75.75 0 01-.75.75H5.612l4.158 3.96a.75.75 0 11-1.04 1.08l-5.5-5.25a.75.75 0 010-1.08l5.5-5.25a.75.75 0 111.04 1.08L5.612 9.25H16.25A.75.75 0 0117 10z"
					clip-rule="evenodd"
				/>
			</svg>
		</div>
		<div class=" self-center font-medium text-sm">{$i18n.t('Back')}</div>
	</button>

	<form
		class="flex flex-col max-w-2xl mx-auto mt-4 mb-10"
		on:submit|preventDefault={() => {
			submitHandler();
		}}
	>
		<input
			id="profile-image-input"
			bind:this={profileImageInputElement}
			type="file"
			hidden
			accept="image/*"
			on:change={(e) => {
				const files = profileImageInputElement.files ?? [];
				let reader = new FileReader();
				reader.onload = (event) => {
					let originalImageUrl = `${event.target.result}`;

					const img = new Image();
					img.src = originalImageUrl;

					img.onload = function () {
						const canvas = document.createElement('canvas');
						const ctx = canvas.getContext('2d');

						// Calculate the aspect ratio of the image
						const aspectRatio = img.width / img.height;

						// Calculate the new width and height to fit within 100x100
						let newWidth, newHeight;
						if (aspectRatio > 1) {
							newWidth = 100 * aspectRatio;
							newHeight = 100;
						} else {
							newWidth = 100;
							newHeight = 100 / aspectRatio;
						}

						// Set the canvas size
						canvas.width = 100;
						canvas.height = 100;

						// Calculate the position to center the image
						const offsetX = (100 - newWidth) / 2;
						const offsetY = (100 - newHeight) / 2;

						// Draw the image on the canvas
						ctx?.drawImage(img, offsetX, offsetY, newWidth, newHeight);

						// Get the base64 representation of the compressed image
						const compressedSrc = canvas.toDataURL('image/jpeg');

						// Display the compressed image
						form_data.image_url = compressedSrc;

						profileImageInputElement.files = null;
					};
				};

				if (
					files.length > 0 &&
					['image/gif', 'image/webp', 'image/jpeg', 'image/png'].includes(files[0]['type'])
				) {
					reader.readAsDataURL(files[0]);
				}
			}}
		/>

		<div class="flex space-x-5">
			<div class="flex flex-col">
				<div class="self-center mt-2">
					<button
						class="relative rounded-full dark:bg-gray-700"
						type="button"
						on:click={() => {
							profileImageInputElement.click();
						}}
					>
						<img
							src={form_data.image_url !== '' ? form_data.image_url : "/user.png"}
							alt="profile"
							class="rounded-full h-24 w-24 object-cover"
						/>

						<div
							class="absolute flex justify-center rounded-full bottom-0 left-0 right-0 top-0 h-full w-full overflow-hidden bg-gray-700 bg-fixed opacity-0 transition duration-300 ease-in-out hover:opacity-50"
						>
							<div class="my-auto text-gray-100">
								<svg
									xmlns="http://www.w3.org/2000/svg"
									viewBox="0 0 20 20"
									fill="currentColor"
									class="w-5 h-5"
								>
									<path
										d="m2.695 14.762-1.262 3.155a.5.5 0 0 0 .65.65l3.155-1.262a4 4 0 0 0 1.343-.886L17.5 5.501a2.121 2.121 0 0 0-3-3L3.58 13.419a4 4 0 0 0-.885 1.343Z"
									/>
								</svg>
							</div>
						</div>
					</button>
				</div>
			</div>

			<div class="flex-1 flex flex-col self-center gap-0.5">
				<div class=" mb-0.5 text-sm font-medium">{$i18n.t('Profile Image')}</div>

				<div>
					<button
						class=" text-xs text-center text-gray-800 dark:text-gray-400 rounded-full px-4 py-0.5 bg-gray-100 dark:bg-gray-850"
						type="button"
						on:click={async () => {
							if (canvasPixelTest()) {
								form_data.image_url = generateInitialsImage(form_data.title);
							} else {
								toast.info(
									$i18n.t(
										'Fingerprint spoofing detected: Unable to use initials as avatar. Defaulting to default profile image.'
									),
									{
										duration: 1000 * 10
									}
								);
							}
						}}>{$i18n.t('Use Initials')}</button
					>

					<button
						class=" text-xs text-center text-gray-800 dark:text-gray-400 rounded-lg px-2 py-1"
						type="button"
						on:click={async () => {
							form_data.image_url = '/user.png';
						}}>{$i18n.t('Remove')}</button
					>
				</div>
			</div>
		</div>

		<div class="my-2">
			<div class=" text-sm font-semibold mb-2">{$i18n.t('Title')}*</div>

			<div>
				<input
					class="px-3 py-1.5 text-sm w-full bg-transparent border dark:border-gray-600 outline-none rounded-lg"
					placeholder={$i18n.t('Add a short title for this prompt')}
					bind:value={form_data.title}
					required
				/>
			</div>
		</div>

		<div class="my-2">
			<div class=" text-sm font-semibold mb-2">{$i18n.t('Command')}*</div>

			<div class="flex items-center mb-1">
				<div
					class="bg-gray-200 dark:bg-gray-600 font-bold px-3 py-1 border border-r-0 dark:border-gray-600 rounded-l-lg"
				>
					/
				</div>
				<input
					class="px-3 py-1.5 text-sm w-full bg-transparent border dark:border-gray-600 outline-none rounded-r-lg"
					placeholder={$i18n.t('short-summary')}
					bind:value={form_data.command}
					required
				/>
			</div>

			<div class="text-xs text-gray-400 dark:text-gray-500">
				{$i18n.t('Only')}
				<span class=" text-gray-600 dark:text-gray-300 font-medium"
					>{$i18n.t('alphanumeric characters and hyphens')}</span
				>
				are allowed. This will be part of the hyperlink to this prompt and cannot be modified in the future.
			</div>
		</div>

		<div class="my-2">
			<div class="flex w-full justify-between">
				<div class=" self-center text-sm font-semibold">{$i18n.t('Prompt Content')}*</div>
			</div>

			<div class="mt-2">
				<div>
					<textarea
						class="px-3 py-1.5 text-sm w-full bg-transparent border dark:border-gray-600 outline-none rounded-lg"
						placeholder={"Write your prompt here."}
						rows="6"
						bind:value={form_data.content}
						required
					/>
				</div>

				<div class="text-xs text-gray-400 dark:text-gray-500">
					ⓘ {$i18n.t('Format your variables using square brackets like this:')}&nbsp;<span
						class=" text-gray-600 dark:text-gray-300 font-medium">[{$i18n.t('variable')}]</span
					>.
					{$i18n.t('Make sure to enclose them with')}
					<span class=" text-gray-600 dark:text-gray-300 font-medium">'['</span>
					{$i18n.t('and')}
					<span class=" text-gray-600 dark:text-gray-300 font-medium">']'</span>.
				</div>

				<div class="text-xs text-gray-400 dark:text-gray-500">
					{$i18n.t('Utilize')}<span class=" text-gray-600 dark:text-gray-300 font-medium">
						{` {{CLIPBOARD}}`}</span
					>
					{$i18n.t('variable to have them replaced with clipboard content.')}
				</div>
			</div>
		</div>

		<div class="my-2">
			<div class=" text-sm font-semibold mb-1">Assigned Classes</div>
			<ClassMultiSelector 
				bind:items={classItems}
				bind:selectedItems={form_data.assigned_classes}
			/>
		</div>

		<!-- <div class="my-2">
			<div class=" text-sm font-semibold mb-1">Deadline</div>
			<label class="dark:bg-gray-900 w-fit rounded py-1 text-xs bg-transparent outline-none text-right">
				<input
					type="checkbox"
					on:change={() => {
						hasDeadline = !hasDeadline;
						if (!hasDeadline) {
							form_data.deadline = null;
						} else {
							form_data.deadline = selectedDateTime;
						}
					}}
					checked={hasDeadline}
				>
				Set deadline for completion.
			</label>
			{#if hasDeadline}
				<DatePicker bind:selectedDateTime={form_data.deadline} placeholder={selectedDateTime} />
			{/if}
		</div>

		<div class="my-2">
			<div class=" text-sm font-semibold mb-1">Evaluation Prompt</div>
			TODO
		</div>

		<div class="my-2">
			<div class=" text-sm font-semibold mb-1">Model</div>
			TODO
		</div>

		<div class="my-2">
			<div class="flex w-full justify-between">
				<div class=" self-center text-sm font-semibold">Additional Information</div>
			</div>

			<div class="mt-2">
				<div>
					<textarea
						class="px-3 py-1.5 text-sm w-full bg-transparent border dark:border-gray-600 outline-none rounded-lg"
						placeholder="Include additional information for the user to refer to in the right sidebar. This supports HTML."
						rows="6"
						bind:value={form_data.additional_info}
					/>
				</div>
				<button class="text-sm px-3 py-2 mt-2 transition rounded-xl bg-gray-50 hover:bg-gray-100 dark:bg-gray-700 dark:hover:bg-gray-800"
					type="button"
					on:click={() => {
						showPreviewModal = !showPreviewModal;
				}}>
					<div class="self-center text-sm font-medium">Preview HTML</div>
				</button>
			</div>
		</div> -->

		<div class="my-2 flex justify-end">
			<button
				class=" text-sm px-3 py-2 mr-2 transition rounded-xl {loading
					? ' cursor-not-allowed bg-gray-100 dark:bg-gray-800'
					: ' bg-gray-50 hover:bg-gray-100 dark:bg-gray-700 dark:hover:bg-gray-800'} flex"
				on:click={() => form_data.is_visible = false}
				type="submit"
				disabled={loading}
			>
				<div class=" self-center font-medium">Save as Draft</div>

				{#if loading}
					<div class="ml-1.5 self-center">
						<svg
							class=" w-4 h-4"
							viewBox="0 0 24 24"
							fill="currentColor"
							xmlns="http://www.w3.org/2000/svg"
							><style>
								.spinner_ajPY {
									transform-origin: center;
									animation: spinner_AtaB 0.75s infinite linear;
								}
								@keyframes spinner_AtaB {
									100% {
										transform: rotate(360deg);
									}
								}
							</style><path
								d="M12,1A11,11,0,1,0,23,12,11,11,0,0,0,12,1Zm0,19a8,8,0,1,1,8-8A8,8,0,0,1,12,20Z"
								opacity=".25"
							/><path
								d="M10.14,1.16a11,11,0,0,0-9,8.92A1.59,1.59,0,0,0,2.46,12,1.52,1.52,0,0,0,4.11,10.7a8,8,0,0,1,6.66-6.61A1.42,1.42,0,0,0,12,2.69h0A1.57,1.57,0,0,0,10.14,1.16Z"
								class="spinner_ajPY"
							/></svg
						>
					</div>
				{/if}
			</button>

			<button
				class=" text-sm px-3 py-2 transition rounded-xl {loading
					? ' cursor-not-allowed bg-emerald-800'
					: ' bg-emerald-700 hover:bg-emerald-800 text-gray-100'} flex"
				on:click={() => form_data.is_visible = true}
				type="submit"
				disabled={loading}
			>
				<div class=" self-center font-medium">{$i18n.t('Save & Create')}</div>

				{#if loading}
					<div class="ml-1.5 self-center">
						<svg
							class=" w-4 h-4"
							viewBox="0 0 24 24"
							fill="currentColor"
							xmlns="http://www.w3.org/2000/svg"
							><style>
								.spinner_ajPY {
									transform-origin: center;
									animation: spinner_AtaB 0.75s infinite linear;
								}
								@keyframes spinner_AtaB {
									100% {
										transform: rotate(360deg);
									}
								}
							</style><path
								d="M12,1A11,11,0,1,0,23,12,11,11,0,0,0,12,1Zm0,19a8,8,0,1,1,8-8A8,8,0,0,1,12,20Z"
								opacity=".25"
							/><path
								d="M10.14,1.16a11,11,0,0,0-9,8.92A1.59,1.59,0,0,0,2.46,12,1.52,1.52,0,0,0,4.11,10.7a8,8,0,0,1,6.66-6.61A1.42,1.42,0,0,0,12,2.69h0A1.57,1.57,0,0,0,10.14,1.16Z"
								class="spinner_ajPY"
							/></svg
						>
					</div>
				{/if}
			</button>
		</div>
	</form>
</div>
