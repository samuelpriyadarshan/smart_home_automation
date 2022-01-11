/*
 * DevUIO.cpp
 *
 *  Created on: 2018/01/16
 *      Author: tak
 */
#include <stdio.h>
#include <stdlib.h>
#include <fcntl.h>
#include <unistd.h>
#include <sys/mman.h>
#include <errno.h>
#include "DevUIO.h"

DevUIO::DevUIO(const char* dev)
{
	/* �������A�N�Z�X�p�̃f�o�C�X�t�@�C�����J�� */
	if ((m_fd = open(dev, O_RDWR | O_SYNC)) < 0) {
		perror("open");
	}

	/* ARM(CPU)���猩�������A�h���X �� ���z�A�h���X�ւ̃}�b�s���O */
	m_address = (void*)mmap(NULL, getpagesize(), PROT_READ | PROT_WRITE, MAP_SHARED, m_fd, 0);
	if (m_address == MAP_FAILED) {
		m_address = NULL;
		perror("mmap");
		close(m_fd);
	}
}

DevUIO::~DevUIO()
{
	/* �g���I��������\�[�X��������� */
	munmap((void*)m_address, getpagesize());
	close(m_fd);
}

bool DevUIO::isValid()
{
	return (m_address != NULL);
}

void DevUIO::writeReg(uint32_t offset, uint32_t data)
{
	*(volatile uint32_t*)((int)m_address + offset) = data;
}

uint32_t DevUIO::readReg(uint32_t offset)
{
	return *(volatile uint32_t*)((int)m_address + offset);
}

