<script lang="ts">
	import { toast } from 'svelte-sonner';
	import { createEventDispatcher } from 'svelte';
	import { onMount, getContext } from 'svelte';
	import { addUser, importUsersExcel } from '$lib/apis/auths';

	import Modal from '../common/Modal.svelte';
	import { WEBUI_BASE_URL } from '$lib/constants';
	import { getRoles } from '$lib/apis/roles';
	import { userRoles } from '$lib/stores';

	const i18n = getContext('i18n');
	const dispatch = createEventDispatcher();

	export let show = false;

	let loading = false;
	let tab = '';
	let inputCSVFiles;
	let inputXLSXFiles;

	let _user = {
		name: '',
		email: '',
		password: '',
		role: 'user'
	};

	$: if (show) {
		_user = {
			name: '',
			email: '',
			password: '',
			role: 'user'
		};
	}

	const submitHandler = async () => {
		const stopLoading = () => {
			dispatch('save');
			loading = false;
		};

		if (tab === '') {
			loading = true;

			const res = await addUser(
				localStorage.token,
				_user.name,
				_user.email,
				_user.password,
				_user.role
			).catch((error) => {
				toast.error(error);
			});

			if (res) {
				stopLoading();
				show = false;
			}
		} else if (tab === "csv_import") {
			if (inputCSVFiles) {
				loading = true;

				const file = inputCSVFiles[0];
				const reader = new FileReader();

				reader.onload = async (e) => {
					const csv = e.target.result;
					const rows = csv.split('\n');

					let userCount = 0;

					for (const [idx, row] of rows.entries()) {
						const columns = row.split(',').map((col) => col.trim());
						console.log(idx, columns);

						if (idx > 0) {
							if (columns.length !== 4) {
								toast.error(`Row ${idx + 1}: invalid format.`);
								continue;
							}
							if (!validRoles.has(columns[3])) {
								toast.error(`Row ${idx + 1}: invalid role, "${columns[3]}" does not exist.`);
								continue;
							}

							const res = await addUser(
								localStorage.token,
								columns[0],
								columns[1],
								columns[2],
								columns[3]
							).catch((error) => {
								toast.error(`Row ${idx + 1}: ${error}`);
								return null;
							});

							if (res) {
								userCount = userCount + 1;
							}
						}
					}

					if (userCount > 0) {
						toast.success(`Successfully imported ${userCount} users.`);
					}

					inputCSVFiles = null;
					const uploadInputElement = document.getElementById('upload-user-csv-input');

					if (uploadInputElement) {
						uploadInputElement.value = null;
					}

					stopLoading();
				};

				reader.readAsText(file);
			} else {
				toast.error($i18n.t('File not found.'));
			}
		} else if (tab === "excel_import") {
			if (inputXLSXFiles) {
				loading = true;

				const file = inputXLSXFiles[0];
				const reader = new FileReader();

				reader.onload = async (e) => {
					const xlsx = e.target.result;
	
					const users = await importUsersExcel(localStorage.token, xlsx)
						.catch((err) => {
							toast.error(err);
							loading = false;
							return null;
						});
					

					if (users.length > 0) {
						toast.success(`Successfully imported ${users.length} users.`);
					}

					inputXLSXFiles = null;
					const uploadInputElement = document.getElementById('upload-user-xlsx-input');

					if (uploadInputElement) {
						uploadInputElement.value = null;
					}

					stopLoading();
				};

				reader.readAsArrayBuffer(file);
			} else {
				toast.error($i18n.t('File not found.'));
			}
		}
	};

	let validRoles: Set<string>;

	onMount(async () => {
		$userRoles = await getRoles(localStorage.token);
		validRoles = new Set($userRoles.map(role => role.name));
	})
</script>

<Modal size="sm" bind:show>
	<div>
		<div class=" flex justify-between dark:text-gray-300 px-5 pt-4 pb-2">
			<div class=" text-lg font-medium self-center">{$i18n.t('Add User')}</div>
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

		<div class="flex flex-col md:flex-row w-full px-5 pb-4 md:space-x-4 dark:text-gray-200">
			<div class=" flex flex-col w-full sm:flex-row sm:justify-center sm:space-x-6">
				<form
					class="flex flex-col w-full"
					on:submit|preventDefault={() => {
						submitHandler();
					}}
				>
					<div class="flex text-center text-sm font-medium rounded-xl bg-transparent/10 p-1 mb-2">
						<button
							class="w-full rounded-lg p-1.5 {tab === '' ? 'bg-gray-50 dark:bg-gray-850' : ''}"
							type="button"
							on:click={() => {
								tab = '';
							}}>Form</button
						>

						<button
							class="w-full rounded-lg p-1 {tab === 'excel_import' ? 'bg-gray-50 dark:bg-gray-850' : ''}"
							type="button"
							on:click={() => {
								tab = 'excel_import';
							}}>Excel Import</button
						>

						<button
							class="w-full rounded-lg p-1 {tab === 'csv_import' ? 'bg-gray-50 dark:bg-gray-850' : ''}"
							type="button"
							on:click={() => {
								tab = 'csv_import';
							}}>CSV Import</button
						>
					</div>
					<div class="px-1">
						{#if tab === ''}
							<div class="flex flex-col w-full">
								<div class=" mb-1 text-xs text-gray-600 dark:text-gray-500">{$i18n.t('Role')}</div>

								<div class="flex-1">
									<select
										class="w-full rounded-lg py-2 px-4 text-sm dark:text-gray-300 dark:bg-gray-850 disabled:text-gray-500 dark:disabled:text-gray-500 outline-none"
										bind:value={_user.role}
										placeholder={$i18n.t('Enter Your Role')}
										required
									>
										{#each $userRoles as role}
											<option value={role.name}> {role.name} </option>
										{/each}
									</select>
								</div>
							</div>

							<div class="flex flex-col w-full mt-2">
								<div class=" mb-1 text-xs text-gray-600 dark:text-gray-500">{$i18n.t('Name')}</div>

								<div class="flex-1">
									<input
										class="w-full rounded-lg py-2 px-4 text-sm dark:text-gray-300 dark:bg-gray-850 disabled:text-gray-500 dark:disabled:text-gray-500 outline-none"
										type="text"
										bind:value={_user.name}
										placeholder={$i18n.t('Enter Your Full Name')}
										autocomplete="off"
										required
									/>
								</div>
							</div>

							<hr class=" dark:border-gray-800 my-3 w-full" />

							<div class="flex flex-col w-full">
								<div class=" mb-1 text-xs text-gray-600 dark:text-gray-500">{$i18n.t('Email')}</div>

								<div class="flex-1">
									<input
										class="w-full rounded-lg py-2 px-4 text-sm dark:text-gray-300 dark:bg-gray-850 disabled:text-gray-500 dark:disabled:text-gray-500 outline-none"
										type="email"
										bind:value={_user.email}
										placeholder={$i18n.t('Enter Your Email')}
										autocomplete="off"
										required
									/>
								</div>
							</div>

							<div class="flex flex-col w-full mt-2">
								<div class=" mb-1 text-xs text-gray-600 dark:text-gray-500">{$i18n.t('Password')}</div>

								<div class="flex-1">
									<input
										class="w-full rounded-lg py-2 px-4 text-sm dark:text-gray-300 dark:bg-gray-850 disabled:text-gray-500 dark:disabled:text-gray-500 outline-none"
										type="password"
										bind:value={_user.password}
										placeholder={$i18n.t('Enter Your Password')}
										autocomplete="off"
									/>
								</div>
							</div>
						{:else if tab === 'excel_import'}
							<div>
								<div class="mb-3 w-full">
									<input
										id="upload-user-xlsx-input"
										hidden
										bind:files={inputXLSXFiles}
										type="file"
										accept=".xlsx"
									/>

									<button
										class="w-full text-sm font-medium py-3 bg-transparent hover:bg-gray-100 border border-dashed dark:border-gray-800 dark:hover:bg-gray-850 text-center rounded-xl"
										type="button"
										on:click={() => {
											document.getElementById('upload-user-xlsx-input')?.click();
										}}
									>
										{#if inputXLSXFiles}
											{inputXLSXFiles.length > 0 
												? `${inputXLSXFiles.length} document selected: ${inputXLSXFiles[0].name}` 
												: '0 documents selected.'}
										{:else}
											Click here to select an xlsx file.
										{/if}
									</button>
								</div>

								<div class=" text-xs text-gray-600 dark:text-gray-500">
									ⓘ Ensure your Excel file includes these 3 columns: Name, Email, Role. <br />
									ⓘ This file can be obtained by exporting from Canvas. <br />
									ⓘ Users successfully imported will be emailed their login details.
								</div>
							</div>
						{:else if tab === 'csv_import'}
							<div>
								<div class="mb-3 w-full">
									<input
										id="upload-user-csv-input"
										hidden
										bind:files={inputCSVFiles}
										type="file"
										accept=".csv"
									/>

									<button
										class="w-full text-sm font-medium py-3 bg-transparent hover:bg-gray-100 border border-dashed dark:border-gray-800 dark:hover:bg-gray-850 text-center rounded-xl"
										type="button"
										on:click={() => {
											document.getElementById('upload-user-csv-input')?.click();
										}}
									>
										{#if inputCSVFiles}
											{inputCSVFiles.length > 0 
												? `${inputCSVFiles.length} document selected: ${inputCSVFiles[0].name}` 
												: '0 documents selected.'}
										{:else}
											{$i18n.t('Click here to select a csv file.')}
										{/if}
									</button>
								</div>

								<div class=" text-xs text-gray-600 dark:text-gray-500">
									ⓘ {$i18n.t(
										'Ensure your CSV file includes 4 columns in this order: Name, Email, Password, Role.'
									)}
									<a
										class="underline dark:text-gray-200"
										href="{WEBUI_BASE_URL}/static/user-import.csv"
									>
										Click here to download user import template file.
									</a>
								</div>
							</div>
						{/if}
					</div>

					<div class="flex justify-end pt-3 text-sm font-medium">
						<button
							class=" px-4 py-2 bg-emerald-400 hover:bg-emerald-500 text-black dark:bg-emerald-700 dark:hover:bg-emerald-800 dark:text-gray-100 transition rounded-lg flex flex-row space-x-1 items-center {loading
								? ' cursor-not-allowed'
								: ''}"
							type="submit"
							disabled={loading}
						>
							{$i18n.t('Submit')}

							{#if loading}
								<div class="ml-2 self-center">
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
		</div>
	</div>
</Modal>

<style>
	input::-webkit-outer-spin-button,
	input::-webkit-inner-spin-button {
		/* display: none; <- Crashes Chrome on hover */
		-webkit-appearance: none;
		margin: 0; /* <-- Apparently some margin are still there even though it's hidden */
	}

	.tabs::-webkit-scrollbar {
		display: none; /* for Chrome, Safari and Opera */
	}

	.tabs {
		-ms-overflow-style: none; /* IE and Edge */
		scrollbar-width: none; /* Firefox */
	}

	input[type='number'] {
		-moz-appearance: textfield; /* Firefox */
	}
</style>
