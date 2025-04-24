$(document).ready(function () {
    const maxImages = 5;

    function updateItemNumbers() {
        $('.item-form').each(function (index) {
            $(this).attr('data-index', index);
            $(this).find('.item-number').text(index + 1);

            // 이미지 컨테이너 및 관련 속성 갱신
            $(this).find('.image-container').attr('id', `image-container-${index}`);
            $(this).find('.add-image').attr('data-index', index);
            $(this).find('.image-management-form').attr('data-index', index);
        });
    }

    // HEIC 변환 및 미리보기 처리
    $(document).on('change', '.image-input', function () {
        const fileInput = this;
        const file = fileInput.files[0];
        const $form = $(fileInput).closest('.image-form');
        const $preview = $form.find('.image-preview');

        if (!file) return;

        $preview.hide();
        let $loader = $form.find('.image-loading');
        if ($loader.length === 0) {
            $loader = $(`
                <div class="image-loading text-center p-2">
                    <div class="spinner-border text-secondary" role="status" style="width: 1.5rem; height: 1.5rem;">
                        <span class="visually-hidden">Loading...</span>
                    </div>
                    <div>변환 중...</div>
                </div>
            `);
            $form.find('.image-preview-wrapper').append($loader);
        }

        if (file.name.toLowerCase().endsWith('.heic')) {
            heic2any({
                blob: file,
                toType: "image/jpeg",
                quality: 0.9
            }).then(function (convertedBlob) {
                const reader = new FileReader();
                reader.onload = function (e) {
                    $preview.attr('src', e.target.result).show();
                    $loader.remove();
                };
                reader.readAsDataURL(convertedBlob);

                const newFile = new File(
                    [convertedBlob],
                    file.name.replace(/\.heic$/i, ".jpg"),
                    { type: "image/jpeg", lastModified: new Date().getTime() }
                );
                const dataTransfer = new DataTransfer();
                dataTransfer.items.add(newFile);
                fileInput.files = dataTransfer.files;
            }).catch(function (err) {
                alert('HEIC 파일 변환 중 오류가 발생했습니다: ' + err.message);
                $loader.html('<div class="text-danger">변환 실패</div>');
            });
            return;
        }

        const reader = new FileReader();
        reader.onload = function (e) {
            $preview.attr('src', e.target.result).show();
            $loader.remove();
        };
        reader.readAsDataURL(file);
    });

    // 클라이언트에서 이미지 삭제
    $(document).on('click', '.delete-image-client', function () {
        const $form = $(this).closest('.image-form');
        const $itemForm = $(this).closest('.item-form');
        const index = $itemForm.data('index');
        const container = $(`#image-container-${index}`);
        $form.remove();

        const updatedCount = container.find('.image-form').length;
        if (updatedCount === 0) {
            alert('최소 한 개의 이미지는 등록해야 합니다.');
            container.append($form); // 복구
        } else {
            $(`input[name="images-${index}-TOTAL_FORMS"]`).val(updatedCount);
        }
    });

    // 서버에 등록된 이미지 삭제
    $(document).on('click', '.delete-image-server', function () {
        const btn = $(this);
        const imageId = btn.data('image-id');
        const $form = btn.closest('.image-form');
        const $itemForm = btn.closest('.item-form');
        const index = $itemForm.data('index');
        const container = $(`#image-container-${index}`);

        if (!confirm('정말 이 이미지를 삭제하시겠습니까?')) return;

        $.ajax({
            url: '/construction/image/delete/',
            type: 'POST',
            data: {
                image_id: imageId,
                csrfmiddlewaretoken: $('[name="csrfmiddlewaretoken"]').val()
            },
            success: function (res) {
                if (res.success) {
                    $form.remove();
                    const updatedCount = container.find('.image-form').length;
                    if (updatedCount === 0) {
                        alert('최소 한 개의 이미지는 등록해야 합니다.');
                        location.reload();  // 서버에서 제거된 상태라 복구 불가, 새로고침
                    } else {
                        $(`input[name="images-${index}-TOTAL_FORMS"]`).val(updatedCount);
                    }
                } else {
                    alert('삭제 실패: ' + res.error);
                }
            },
            error: function (xhr) {
                alert('에러 발생: ' + xhr.responseText);
            }
        });
    });

    $(document).on('click', '.add-image', function () {
        const index = $(this).data('index');
        const $container = $(`#image-container-${index}`);
        const totalFormsInput = $(`input[name="images-${index}-TOTAL_FORMS"]`);

        let currentCount = $container.find('.image-form').length;

        if (currentCount >= 5) {
            alert('이미지는 품목당 최대 5개까지만 추가할 수 있습니다.');
            return;
        }

        // 첫 번째 이미지 form을 복제 (image-form 안에 input 파일 있고, 필요시 삭제 버튼 포함)
        const $newForm = $container.find('.image-form:first').clone(true, true);

        // input name/id 및 값 초기화
        $newForm.find('input').each(function () {
            const $input = $(this);
            if ($input.attr('type') === 'hidden' && $input.attr('name')?.includes('DELETE')) {
                $input.remove();
                return;
            }
            const name = $input.attr('name');
            const id = $input.attr('id');

            if (name) $input.attr('name', name.replace(/images-\d+-\d+/, `images-${index}-${currentCount}`));
            if (id) $input.attr('id', id.replace(/id_images-\d+-\d+/, `id_images-${index}-${currentCount}`));
            $input.val('');
        });

        // 이미지 프리뷰 초기화
        $newForm.find('.image-preview').remove();
        $newForm.find('.delete-image-server').remove();

        $container.find('.add-image').parent().before($newForm); // 버튼 위에 삽입
        totalFormsInput.val(currentCount + 1);
    });

    // 품목 삭제
    $(document).on('click', '.delete-item', function () {
        const $itemForm = $(this).closest('.item-form');
        const $deleteCheckbox = $itemForm.find('input[type="checkbox"][name$="-DELETE"]');
        if ($deleteCheckbox.length) {
            $itemForm.hide();
            $deleteCheckbox.prop('checked', true);
        } else {
            $itemForm.remove();
            $('#id_items-TOTAL_FORMS').val($('.item-form').length);
            updateItemNumbers();
        }
    });

    // 품목 추가
    const totalItemsInput = $('#id_items-TOTAL_FORMS');
    const itemContainer = $('#formset-container');
    const itemTemplate = itemContainer.children('.item-form:first').clone();

    itemTemplate.find('input, select, textarea').val('');
    itemTemplate.find('.image-preview').hide().attr('src', '');
    itemTemplate.find('.image-loading').remove();
    itemTemplate.find('.image-form').not(':first').remove();

    $('#add-item-btn').on('click', function () {
        let formIdx = parseInt(totalItemsInput.val());
        const newItem = itemTemplate.clone();

        // 필드 업데이트
        newItem.find('input, select, textarea').each(function () {
            const name = $(this).attr('name');
            const id = $(this).attr('id');
            if (name) {
                $(this).attr('name', name
                    .replace(/items-\d+-/g, `items-${formIdx}-`)
                    .replace(/images-\d+-\d+-/g, `images-${formIdx}-0-`)
                    .replace(/images-\d+-/g, `images-${formIdx}-`));
            }
            if (id) {
                $(this).attr('id', id
                    .replace(/id_items-\d+-/g, `id_items-${formIdx}-`)
                    .replace(/id_images-\d+-\d+-/g, `id_images-${formIdx}-0-`)
                    .replace(/id_images-\d+-/g, `id_images-${formIdx}-`));
            }
            $(this).val('');
        });

        newItem.find('input[name$="-id"]').val('');
        newItem.find('.image-preview').hide().attr('src', '');
        newItem.find('.image-loading').remove();
        newItem.find('.image-form').not(':first').remove();

        newItem.find('.image-input').off('change').on('change'); // 방지

        const imageContainer = newItem.find('.image-container');
        imageContainer.attr('id', `image-container-${formIdx}`);
        newItem.find('.add-image').attr('data-index', formIdx);

        // 이미지 관리 폼 복제
        const mgmtFormSource = $('.image-management-form[data-index="0"]').clone();
        mgmtFormSource.attr('data-index', formIdx);
        mgmtFormSource.find('input[type="hidden"]').each(function () {
            const newName = $(this).attr('name').replace(/images-0-/, `images-${formIdx}-`);
            const newId = $(this).attr('id').replace(/id_images-0-/, `id_images-${formIdx}-`);
            $(this).attr('name', newName).attr('id', newId);

            if (newName.endsWith('-TOTAL_FORMS')) $(this).val('1');
            if (newName.endsWith('-INITIAL_FORMS')) $(this).val('0');
        });

        imageContainer.before(mgmtFormSource);

        // 첫 번째 이미지 필드 재설정
        newItem.find('.image-form:first input').each(function () {
            const name = $(this).attr('name');
            const id = $(this).attr('id');
            if (name && id) {
                $(this).attr({
                    name: name.replace(/images-\d+-\d+-/, `images-${formIdx}-0-`),
                    id: id.replace(/id_images-\d+-\d+-/, `id_images-${formIdx}-0-`)
                }).val('');
            }
        });

        itemContainer.append(newItem);
        totalItemsInput.val(formIdx + 1);
        updateItemNumbers();
    });

    // CSRF token 전역 설정
    $.ajaxSetup({
        headers: {
            'X-CSRFToken': $('meta[name="csrf-token"]').attr('content')
        }
    });
});
