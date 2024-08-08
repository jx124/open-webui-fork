<script lang="ts">
	import { toast } from 'svelte-sonner';

	import { onMount, getContext } from 'svelte';
	import UserSelector from '$lib/components/workspace/UserSelector.svelte';
	import { getUsers } from '$lib/apis/users';
	import { type ClassForm, getClassById, updateClass } from '$lib/apis/classes';
	import { goto } from '$app/navigation';
	import { page } from '$app/stores';
	import { prompts } from '$lib/stores';
	import { getPrompts } from '$lib/apis/prompts';
	import PromptMultiSelector from '$lib/components/workspace/PromptMultiSelector.svelte';

	const i18n = getContext('i18n');

    let form_data: ClassForm = {
		id: 0,
		name: "",
		instructor_id: ""
	};

    let instructorName = "";

    let pageLoading = false;
    let loading = false;

	const submitHandler = async () => {
		loading = true;

        const class_ = await updateClass(localStorage.token, form_data).catch((error) => {
			toast.error(error);
		});

		loading = false;

        if (class_) {
			toast.success('Class updated successfully');
		}
	};

    let items: {
        value: string,
        label: string
    }[];

    let promptItems: {
        value: number,
        label: string
    }[];

    onMount(async () => {
        pageLoading = true;

        form_data.id = parseInt($page.url.searchParams.get("id") ?? "0");

        const class_ = await getClassById(localStorage.token, form_data.id).catch((error) => {
            loading = false;
            toast.error(error);
            goto('/workspace/classes');
        });

        form_data.name = class_.name;
        form_data.instructor_id = class_.instructor_id;
        instructorName = class_.instructor_name;

        const users = await getUsers(localStorage.token).catch((error) => {
			pageLoading = false;
			toast.error(error);
		});

        const validUsers = users?.filter(user => ["admin", "instructor"].includes(user.role));
        items = validUsers?.map(user => { 
            return {
                value: user.id,
                label: user.name
            };
        })

		$prompts = await getPrompts(localStorage.token).catch((error) => {
			pageLoading = false;
			toast.error(error);
		});

		promptItems = $prompts?.map(prompt => { 
            return {
                value: prompt.id,
                label: prompt.title
            };
        })

        pageLoading = false;
    });
</script>

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

    {#if pageLoading}
        <div class="flex h-full">
            <div class="flex mx-auto items-center self-center">
                <svg
                    class=" w-8 h-8"
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
                <span class="ml-2">
                    Loading...
                </span>
            </div>
        </div>
    {:else}
        <form
            class="flex flex-col max-w-2xl mx-auto mt-4 mb-10"
            on:submit|preventDefault={() => {
                submitHandler();
            }}
        >
            <div class="my-2">
                <div class=" text-sm font-semibold mb-2">{$i18n.t('Name')}*</div>

                <div>
                    <input
                        class="px-3 py-1.5 text-sm w-full bg-transparent border dark:border-gray-600 outline-none rounded-lg"
                        placeholder={"Add a name for this class"}
                        bind:value={form_data.name}
                        required
                    />
                </div>
            </div>

            <div class="my-2">
                <div class=" text-sm font-semibold mb-2">Instructor*</div>

                <UserSelector 
                    bind:value={form_data.instructor_id}
                    externalLabel={instructorName}
                    {items}
                    placeholder={"Select an instructor"}
                    searchPlaceholder={"Search for an instructor"}
                />
            </div>

            <div class="my-2">
                <div class=" text-sm font-semibold mb-2">Students</div>
            </div>

            <div class="my-2">
                <div class=" text-sm font-semibold mb-2">Prompts</div>
                <PromptMultiSelector 
					addItemLabel={"Add Prompt"}
					searchPlaceholder={"Search Prompts"} 
					bind:items={promptItems}
					bind:selectedItems={form_data.assigned_prompts}
				/>
            </div>

            <div class="my-2 flex justify-end">
                <button
                    class=" text-sm px-3 py-2 transition rounded-xl {loading
                        ? ' cursor-not-allowed bg-gray-100 dark:bg-gray-800'
                        : ' bg-gray-50 hover:bg-gray-100 dark:bg-gray-700 dark:hover:bg-gray-800'} flex"
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
    {/if}
</div>
