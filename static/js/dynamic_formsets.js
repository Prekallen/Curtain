$(document).ready(function () {
    const maxImages = 5;
    const maxItems = 10;
    const minImages = 1;
    const minItems = 1;

    // 품목 및 이미지의 Index를 업데이트
    function updateItemNumbers() {
        $('.item-form').each(function (index) {
            $(this).attr('data-index', index);
            $(this).find('.item-number').text(index + 1);

            // 이미지 컨테이너 및 관련 속성 갱신
            $(this).find('.image-container').attr('id', `image-container-${index}`);
            $(this).find('.add-image').attr('data-index', index);

            // 관리 필드 업데이트
            $(this)
                .find('input[name$="-TOTAL_FORMS"]')
                .attr('name', `images-${index}-TOTAL_FORMS`);
            $(this)
                .find('input[name$="-INITIAL_FORMS"]')
                .attr('name', `images-${index}-INITIAL_FORMS`);

            // 이미지 필드 Name/ID 업데이트
            $(this).find('.image-form').each(function (imgIndex) {
                $(this)
                    .find('input')
                    .each(function () {
                        const name = $(this).attr('name');
                        const id = $(this).attr('id');
                        if (name) {
                            $(this).attr(
                                'name',
                                name.replace(/images-\d+-\d+/, `images-${index}-${imgIndex}`)
                            );
                        }
                        if (id) {
                            $(this).attr(
                                'id',
                                id.replace(/id_images-\d+-\d+/, `id_images-${index}-${imgIndex}`)
                            );
                        }
                    });
            });
        });
        // 품목 관리 필드 갱신
        $('#id_items-TOTAL_FORMS').val($('.item-form').length);
    }

    // 이미지 추가
    $('#add-image-btn').off('click').on('click', function () {
        const index = $(this).data('index');
        const $container = $(`#image-container-${index}`);
        const totalFormsInput = $container.find(`input[name="images-${index}-TOTAL_FORMS"]`);

        console.log('이미지 추가 버튼 클릭');
        
        const currentCount = $container.find('.image-form').length;

        if (currentCount >= maxImages) {
            alert('이미지는 품목당 최대 5개까지만 추가할 수 있습니다.');
            return;
        }

        // 첫 번째 이미지 Form 복제
        const $newForm = $container.find('.image-form:first').clone(false);

        // Input 초기화
        $newForm.find('input').val('');
        $newForm.find('.image-preview').hide();

        // Name/ID 갱신
        $newForm.find('input').each(function () {
            const name = $(this).attr('name');
            const id = $(this).attr('id');
            if (name) {
                $(this).attr(
                    'name',
                    name.replace(/images-\d+-\d+/, `images-${index}-${currentCount}`)
                );
            }
            if (id) {
                $(this).attr(
                    'id',
                    id.replace(/id_images-\d+-\d+/, `id_images-${index}-${currentCount}`)
                );
            }
        });

        $container.append($newForm);
        totalFormsInput.val(currentCount + 1); // 관리 필드 값 갱신
    });

    // 이미지 삭제
    $(document).off('click', '.delete-image-client').on('click', '.delete-image-client', function () {
        const $form = $(this).closest('.image-form');
        const $container = $form.closest('.image-container');
        const index = $container.data('index');

        if ($container.find('.image-form').length <= minImages) {
            alert('최소 한 개의 이미지는 등록해야 합니다.');
            return;
        }

        $form.remove();
        const updatedCount = $container.find('.image-form').length;

        // 관리 필드 갱신
        $container
            .find(`input[name="images-${index}-TOTAL_FORMS"]`)
            .val(updatedCount);

        updateItemNumbers();
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

    // 품목 삭제
    $(document).off('click', '.delete-item').on('click', '.delete-item', function () {
        const $itemForms = $('#formset-container .item-form:visible');
        const $itemForm = $(this).closest('.item-form');
        let totalItems = $itemForms.length;

        if (totalItems <= minItems) {
            alert('품목은 최소 1개 이상 있어야 합니다.');
            return;
        }

        console.log('현재 품목 개수:', totalItems);

        // 삭제 확인
        if (!confirm('정말 이 품목을 삭제하시겠습니까?')) {
            return; // 취소 시 삭제 중단
        }

        // 삭제 처리
        const $deleteInput = $itemForm.find('[name$="-DELETE"]');
        if ($deleteInput.length) {
            // Django 폼셋의 DELETE 체크박스가 있는 경우
            $deleteInput.val('on'); // 삭제 플래그 설정
            $itemForm.hide(); // UI에서 숨기기
        } else {
            // DELETE 직접 제거
            $itemForm.remove();
            alert("삭제 체크박스를 찾을 수 없습니다. 폼 삭제가 처리되지 않았습니다.");
        }

        // 삭제 후 품목 개수 재확인 및 업데이트
        // 삭제 후 DOM 상태 다시 확인
        totalItems = $('#formset-container .item-form:visible').length; // 최신 item-form 개수 재확인
        console.log('삭제 후 품목 개수:', totalItems);

        // 총 폼 개수를 Django 관리 필드에 반영
        $('#id_items-TOTAL_FORMS').val($itemForm.length - 1);

        updateItemNumbers();
    });

    // 품목 추가
    $('#add-item-btn').off('click').on('click', function (){
        const totalItemsInput = $('#id_items-TOTAL_FORMS');
        const currentCount = parseInt(totalItemsInput.val(), 10);
        const $itemTemplate = $('#formset-container')
            .find('.item-form:first')
            .clone(false);

        // 최대 품목 수 제한 로직
        if (currentCount >= maxItems) {
            alert(`최대 품목 수는 ${maxItems}개입니다.`);
            return; // 추가를 중단
        }

        // Input 초기화
        $itemTemplate.find('input, select, textarea').val('');
        $itemTemplate.find('.image-preview').hide();
        $itemTemplate.find('.image-form:not(:first)').remove(); // 첫 번째만 유지

        // 인덱스 갱신
        $itemTemplate
            .find('input, select, textarea')
            .each(function () {
                const name = $(this).attr('name');
                const id = $(this).attr('id');
                if (name) {
                    $(this).attr(
                        'name',
                        name.replace(/items-\d+/g, `items-${currentCount}`)
                    );
                }
                if (id) {
                    $(this).attr(
                        'id',
                        id.replace(/id_items-\d+/g, `id_items-${currentCount}`)
                    );
                }
            });

        $itemTemplate
            .find('.image-container')
            .attr('id', `image-container-${currentCount}`)
            .find('input[name="images-0-TOTAL_FORMS"]')
            .val(1);

        $('#formset-container').append($itemTemplate);

        totalItemsInput.val(currentCount + 1); // 관리 필드 갱신
        updateItemNumbers();
    });

    // CSRF token 전역 설정
    $.ajaxSetup({
        headers: {
            'X-CSRFToken': $('meta[name="csrf-token"]').attr('content')
        }
    });

    // 파일 선택 시 미리보기 업데이트
    $(document).on('change', '.image-input', function () {
        const fileInput = this;
        const file = fileInput.files[0];
        const $form = $(fileInput).closest('.image-form');
        const $preview = $form.find('.image-preview');

        // 파일이 없으면 초기화 후 종료
        if (!file) {
            $preview.hide().attr('src', '');
            $form.find('.image-loading').remove();
            return;
        }

        // 1. 미리보기와 로딩 상태 초기화 및 로더 표시
        $preview.hide().attr('src', '');
        let $loader = $form.find('.image-loading');

        // 로더가 없으면 생성하여 추가
        if ($loader.length === 0) {
            $loader = $(`
            <div class="image-loading text-center p-2">
                <div class="spinner-border text-secondary" role="status" style="width: 1.5rem; height: 1.5rem;">
                    <span class="visually-hidden">Loading...</span>
                </div>
                <div class="small mt-1">이미지 처리 중...</div>
            </div>
        `);
            $form.find('.image-preview-wrapper').append($loader);
        }
        $loader.show(); // 로더를 다시 표시

        const fileName = file.name.toLowerCase();

        // 2. HEIC 파일 처리 (heic2any 사용)
        if (fileName.endsWith('.heic') || fileName.endsWith('.heif')) {

            // heic2any가 로드되지 않았을 경우 (CDN/스크립트 로드 실패 시) 경고
            if (typeof heic2any === 'undefined') {
                alert('HEIC 변환 라이브러리가 로드되지 않았습니다. HEIC 미리보기가 불가합니다.');
                $loader.html('<div class="text-danger small">라이브러리 로드 실패</div>');
                return;
            }

            // heic2any를 사용하여 Blob을 JPEG로 변환
            heic2any({
                blob: file,
                toType: 'image/jpeg',
                quality: 0.9,
            })
                .then(function (conversionResult) {
                    // 변환 성공 시
                    const url = URL.createObjectURL(conversionResult);
                    $preview.attr('src', url).show();
                    $loader.remove(); // 로더 제거
                })
                .catch(function (error) {
                    // 변환 실패 시
                    console.error("HEIC 변환 오류 (클라이언트):", error);
                    $loader.html('<div class="text-danger small">변환 실패</div>');
                    alert('HEIC 파일 미리보기에 실패했습니다. 다른 포맷을 사용하거나 서버에 문의하세요.');
                });

            return;
        }

        // 3. HEIC 이외의 파일 처리 (기존 로직 유지)
        const reader = new FileReader();
        reader.onload = function (e) {
            // 일반 이미지 파일 미리보기
            $preview.attr('src', e.target.result).show();
            $loader.remove(); // 로더 제거
        };
        reader.onerror = function () {
            $loader.html('<div class="text-danger small">파일 읽기 오류</div>');
        };
        reader.readAsDataURL(file);
    });

    // 초기화
    updateItemNumbers();
});
